/*
 * SmartWaste360 — IoT Bin Fill-Level Monitor
 * Hardware: ESP32 DevKit V1 + HC-SR04 Ultrasonic Sensor
 * 
 * Wiring (with voltage divider for ECHO):
 *   HC-SR04 VCC  → ESP32 VIN (5V from USB)
 *   HC-SR04 GND  → ESP32 GND
 *   HC-SR04 TRIG → ESP32 GPIO 5
 *   HC-SR04 ECHO → [1kΩ resistor] → ESP32 GPIO 18
 *                                  ↓
 *                              [2kΩ resistor]
 *                                  ↓
 *                                 GND
 * 
 * Pipeline:
 *   Sensor → ESP32 → WiFi → POST /api/iot/bin-level → PostgreSQL → Dashboard
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>  // Needed for HTTPS (Render)

// ============================
// CONFIGURATION — CHANGE THESE
// ============================

const char* WIFI_SSID     = "Kamui";
const char* WIFI_PASSWORD = "vamd4666";

// Backend URL — PICK ONE:
// Option A: Local (for development + demo/viva — fast, reliable)
//   Find your IP with: ipconfig (Windows) or ifconfig (Mac/Linux)
// const char* SERVER_URL = "http://10.101.13.222:5000/api/iot/bin-level";
//
// Option B: Deployed Render (works from any WiFi)
const char* SERVER_URL = "https://smartwaste360-backend.onrender.com/api/iot/bin-level";

// Must match IOT_API_KEY in your backend .env / iot.py
const char* IOT_API_KEY = "smartwaste-iot-demo-key-2026";

// Device identity
const char* DEVICE_ID   = "BIN-001";
const char* POINT_NAME  = "hii";        // Collection point name on your website
int         COLONY_ID   = 1;            // Which colony this bin belongs to
const char* WASTE_TYPE  = "plastic";    // What type of waste this bin collects

// Bin dimensions
const float BIN_HEIGHT_CM   = 30.0;   // Distance from sensor to bin bottom (cm)
const float BIN_CAPACITY_KG = 10.0;   // Max weight when bin is 100% full

// Sensor pins
const int TRIG_PIN = 5;
const int ECHO_PIN = 18;

// Timing
const int SEND_INTERVAL_MS = 5000;    // 5 seconds (matches frontend poll rate)

// ============================
// RELIABILITY SETTINGS
// ============================

// Noise filtering: take N readings and use the median (removes spikes)
const int   NUM_SAMPLES          = 5;      // Number of readings per measurement
const int   SAMPLE_DELAY_MS      = 50;     // Gap between samples (ms)

// Smart send: skip sending if fill level hasn't changed much
const float CHANGE_THRESHOLD_PCT = 2.0;    // Only send if fill changed by >2%

// Sensor bounds: ignore readings outside physical range
const float MIN_VALID_DISTANCE   = 2.0;    // HC-SR04 minimum range (cm)
const float MAX_VALID_DISTANCE   = 200.0;  // HC-SR04 max useful range (cm)

// WiFi retry
const int   WIFI_MAX_RETRIES     = 3;      // Retries per send attempt
const int   WIFI_RETRY_DELAY_MS  = 2000;   // Wait between retries

// ============================
// STATE VARIABLES
// ============================

float lastSentFillPct    = -1.0;   // Track last sent value for smart-send
int   consecutiveErrors  = 0;      // Track sensor failures
int   successfulSends    = 0;      // Stats counter
int   failedSends        = 0;      // Stats counter

// ============================
// SETUP
// ============================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("==========================================");
  Serial.println("  SmartWaste360 IoT Bin Monitor v2.0");
  Serial.println("  ESP32 + HC-SR04 (Voltage Divider)");
  Serial.println("==========================================");
  Serial.printf("  Device:     %s\n", DEVICE_ID);
  Serial.printf("  Colony:     %d\n", COLONY_ID);
  Serial.printf("  Waste Type: %s\n", WASTE_TYPE);
  Serial.printf("  Bin Height: %.0f cm\n", BIN_HEIGHT_CM);
  Serial.printf("  Capacity:   %.0f kg\n", BIN_CAPACITY_KG);
  Serial.printf("  Server:     %s\n", SERVER_URL);
  Serial.printf("  Interval:   %d ms\n", SEND_INTERVAL_MS);
  Serial.printf("  Samples:    %d per reading\n", NUM_SAMPLES);
  Serial.println("==========================================");
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  connectWiFi();
  
  Serial.println("[OK] Setup complete. Starting measurements...\n");
}

// ============================
// MAIN LOOP
// ============================

void loop() {
  // 1. Get filtered distance (median of N samples)
  float distance_cm = getFilteredDistance();
  
  // 2. Handle sensor failure
  if (distance_cm < 0) {
    consecutiveErrors++;
    Serial.printf("[WARN] Sensor error #%d\n\n", consecutiveErrors);
    
    // After 5 consecutive errors, still send a report so backend knows device is alive
    if (consecutiveErrors >= 5) {
      Serial.println("[ALERT] Sensor may be disconnected — sending error report");
      sendToServer(-1.0, 0.0, -1.0);
      consecutiveErrors = 0;
    }
    
    delay(SEND_INTERVAL_MS);
    return;
  }
  
  consecutiveErrors = 0;  // Reset on successful read
  
  // 3. Calculate fill percentage
  float fill_percentage = 0.0;
  
  if (distance_cm >= BIN_HEIGHT_CM) {
    fill_percentage = 0.0;    // Bin is empty (sensor sees the bottom)
  } else if (distance_cm <= MIN_VALID_DISTANCE) {
    fill_percentage = 100.0;  // Bin is overflowing
  } else {
    fill_percentage = ((BIN_HEIGHT_CM - distance_cm) / BIN_HEIGHT_CM) * 100.0;
  }
  
  fill_percentage = constrain(fill_percentage, 0.0, 100.0);
  
  // 4. Estimate weight
  float estimated_weight_kg = (fill_percentage / 100.0) * BIN_CAPACITY_KG;
  
  // 5. Print reading
  Serial.println("--- Reading ---");
  Serial.printf("  Distance:   %.1f cm\n", distance_cm);
  Serial.printf("  Fill:       %.1f %%\n", fill_percentage);
  Serial.printf("  Weight:     %.2f kg\n", estimated_weight_kg);
  
  // 6. Smart send: only transmit if value changed significantly
  float change = abs(fill_percentage - lastSentFillPct);
  bool isFirstSend = (lastSentFillPct < 0);
  
  if (isFirstSend || change >= CHANGE_THRESHOLD_PCT) {
    Serial.printf("  Change:     %.1f%% (threshold: %.1f%%) → SENDING\n", change, CHANGE_THRESHOLD_PCT);
    
    if (WiFi.status() == WL_CONNECTED) {
      bool success = sendToServer(fill_percentage, estimated_weight_kg, distance_cm);
      if (success) {
        lastSentFillPct = fill_percentage;
      }
    } else {
      Serial.println("  [WARN] WiFi lost — reconnecting...");
      connectWiFi();
      // Try sending after reconnect
      if (WiFi.status() == WL_CONNECTED) {
        if (sendToServer(fill_percentage, estimated_weight_kg, distance_cm)) {
          lastSentFillPct = fill_percentage;
        }
      }
    }
  } else {
    Serial.printf("  Change:     %.1f%% (threshold: %.1f%%) → SKIPPED (no change)\n", change, CHANGE_THRESHOLD_PCT);
  }
  
  Serial.printf("  Stats:      %d sent, %d failed\n\n", successfulSends, failedSends);
  
  delay(SEND_INTERVAL_MS);
}

// ============================
// SENSOR: Filtered Reading
// ============================

float getFilteredDistance() {
  /*
   * Takes NUM_SAMPLES readings, sorts them, returns the MEDIAN.
   * The median naturally ignores outlier spikes from the HC-SR04
   * (which are common — the sensor occasionally returns 0 or wild values).
   */
  float samples[NUM_SAMPLES];
  int validCount = 0;
  
  for (int i = 0; i < NUM_SAMPLES; i++) {
    float d = readSingleDistance();
    
    // Only keep readings within the sensor's valid range
    if (d >= MIN_VALID_DISTANCE && d <= MAX_VALID_DISTANCE) {
      samples[validCount] = d;
      validCount++;
    }
    
    delay(SAMPLE_DELAY_MS);
  }
  
  // If more than half the samples failed, sensor has a problem
  if (validCount < (NUM_SAMPLES / 2 + 1)) {
    Serial.printf("  [WARN] Only %d/%d valid samples\n", validCount, NUM_SAMPLES);
    return -1.0;
  }
  
  // Sort for median (simple bubble sort — N is tiny)
  for (int i = 0; i < validCount - 1; i++) {
    for (int j = i + 1; j < validCount; j++) {
      if (samples[j] < samples[i]) {
        float tmp = samples[i];
        samples[i] = samples[j];
        samples[j] = tmp;
      }
    }
  }
  
  // Return median
  float median = samples[validCount / 2];
  return median;
}

float readSingleDistance() {
  // Trigger pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read echo (timeout 30ms ≈ 5m max range)
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  
  if (duration == 0) {
    return -1.0;  // Timeout
  }
  
  // Speed of sound = 343 m/s = 0.0343 cm/µs
  // Distance = (time * speed) / 2
  return (duration * 0.0343) / 2.0;
}

// ============================
// NETWORK
// ============================

void connectWiFi() {
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);          // Station mode (client)
  WiFi.disconnect();             // Clear old connection
  delay(100);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WiFi] FAILED — check SSID/password, or move closer to router");
  }
}

bool sendToServer(float fill_percentage, float weight_kg, float distance_cm) {
  // Detect if URL is HTTPS
  bool isHTTPS = String(SERVER_URL).startsWith("https");
  
  // Retry loop for reliability
  for (int attempt = 1; attempt <= WIFI_MAX_RETRIES; attempt++) {
    HTTPClient http;
    
    WiFiClientSecure *client = nullptr;

    if (isHTTPS) {
      // HTTPS: use WiFiClientSecure (skip cert check — fine for demo)
      client = new WiFiClientSecure;
      client->setInsecure();  // Skip SSL certificate verification
      http.begin(*client, SERVER_URL);
    } else {
      // HTTP: direct connection (local Flask)
      http.begin(SERVER_URL);
    }
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-IoT-API-Key", IOT_API_KEY);
    http.setTimeout(10000);  // 10 second timeout
    
    // Build JSON using snprintf to avoid String heap fragmentation
    char payload[256];
    snprintf(payload, sizeof(payload), 
             "{\"device_id\":\"%s\",\"point_name\":\"%s\",\"colony_id\":%d,\"waste_type\":\"%s\",\"fill_percentage\":%.1f,\"estimated_weight_kg\":%.2f,\"distance_cm\":%.1f,\"bin_height_cm\":%.1f,\"battery_level\":100}",
             DEVICE_ID, POINT_NAME, COLONY_ID, WASTE_TYPE, fill_percentage, weight_kg, distance_cm, BIN_HEIGHT_CM);
    
    if (attempt == 1) {
      Serial.printf("  POST → %s\n", SERVER_URL);
    }
    
    int httpCode = http.POST(payload);
    
    if (httpCode == 200) {
      String response = http.getString();
      Serial.printf("  [OK] Server 200: %s\n", response.c_str());
      http.end();
      if (client) { delete client; }
      successfulSends++;
      return true;
    }
    
    // Non-200 response or connection failure
    if (httpCode > 0) {
      Serial.printf("  [ERR] Server %d (attempt %d/%d)\n", httpCode, attempt, WIFI_MAX_RETRIES);
    } else {
      Serial.printf("  [ERR] %s (attempt %d/%d)\n", http.errorToString(httpCode).c_str(), attempt, WIFI_MAX_RETRIES);
    }
    
    http.end();
    if (client) { delete client; }
    
    if (attempt < WIFI_MAX_RETRIES) {
      delay(WIFI_RETRY_DELAY_MS);
    }
  }
  
  failedSends++;
  Serial.println("  [FAIL] All retries exhausted");
  return false;
}
