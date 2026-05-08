# Codebase Bug Report

This document outlines the bugs and issues identified during the analysis of the SmartWaste360 repository. The findings are categorized into Backend, Frontend, and IoT components, with an assessment of their severity (Critical, Functionality, Syntax/Improvement).

---

## 1. Backend (Flask, Python)

### Critical
* **Insecure Default Secret Keys**: The `SECRET_KEY` and `JWT_SECRET_KEY` in `app.py` default to insecure values (`dev-only-insecure-key-change-in-production`, etc.). While they attempt to load from environment variables, fallback values in production code pose a severe security risk if the `.env` configuration fails.
* **Database Connection Leaks**: The `config/database.py` file uses a basic connection pool (`psycopg2.pool.SimpleConnectionPool`), but if `db.commit()` or `db.cursor()` throws an exception in model methods (e.g., `user.py`, `colony.py`), the connection may not be properly returned to the pool or closed. We should use `contextlib.contextmanager` or ensure `finally` blocks handle pool releases properly.
* **Missing Error Details**: Many try-except blocks (e.g. in `routes/auth.py`, `routes/admin.py`, `routes/collector.py`) catch generic `Exception as e` and return `{'error': 'An internal server error occurred'}`. While good for hiding stack traces from users, the actual error is often lost or only printed via `traceback.print_exc()`, which makes production debugging difficult. They should use a proper logging framework.

### Functionality
* **Empty `except` blocks (Silenced Errors)**: Several files have empty `except` blocks or `except Exception: pass` (e.g., `routes/booking.py` line 55, `routes/collector.py` line 61). This silences errors completely, making issues impossible to diagnose.
* **Inconsistent JWT Error Handling**: Some routes (e.g. `routes/booking.py`, `routes/collector.py`) have code like `except Exception: pass` when verifying JWT roles via `get_jwt()`. This means if the token lacks a role claim, or is malformed, it silently continues and may try to access `collector_id = get_jwt_identity()`, which could lead to unauthorized access or crashes later in the route.
* **Incorrect Error handling with OpenStreetMap API**: In `backend/models/colony.py`, `_get_city_state_from_coords` catches generic exceptions with an empty `except:` block (bare except), which is a Python anti-pattern and can catch `KeyboardInterrupt` or `SystemExit`.
* **Missing Location Columns Check**: There's a `TODO` in `backend/models/collector.py` regarding adding location columns to the collectors table if needed, which indicates incomplete features.

### Syntax/Improvement
* **Redundant/Debug Print Statements**: There are many `print()` statements scattered throughout the codebase (e.g., `routes/waste.py`, `services/ml_service.py`), which should be replaced with `logging`.
* **Hardcoded Model Labels**: In `services/ml_service.py`, `class_labels` are hardcoded. This makes updating the ML model or adding new waste types require a code change rather than a configuration change.

---

## 2. Frontend (React, JS)

### Critical
* **Error Handling in Promises**: Several services (e.g., `services/waste.js`, `services/user.js`) catch errors and immediately throw them again or throw generic `Error` objects without exposing the underlying cause, making the frontend unresponsive or showing generic "Error" text when an API call fails.
* **Unsafe Local Storage Access**: `localStorage.getItem` and `setItem` are used directly (e.g., in `AuthContext.jsx` and `services/auth.js`) without `try/catch` blocks. In some environments (like incognito mode or restricted iframes), accessing `localStorage` throws a QuotaExceededError or SecurityError, breaking the app.

### Functionality
* **Console Errors without State Update**: In components like `UserStats.jsx`, `WasteHistory.jsx`, and `CollectorStatsWidget.jsx`, the `catch` blocks log errors to the console (`console.error("Error fetching stats")`) but do not set an error state to inform the user. The UI will just show an empty state or infinite loading indicator if `finally` block logic is missing.
* **Missing Dependency Array in `useEffect`**: In `AdminDashboard.jsx`, the `loadCollectors` dependency array is missing or incorrect, potentially causing stale closures or infinite loops if state updates trigger re-renders.
* **Role Check Flaws**: In `AuthContext.jsx`, the `adminLoginAction` assumes if `response.data.access_token` is present, it should just pick `response.data.admin || response.data.user`. If a regular user logs in via the admin portal, they might bypass UI restrictions depending on how the backend returns data.

### Syntax/Improvement
* **Debug Logs Left in Code**: There are numerous `console.log()` statements left in production code (e.g., `console.log('🔍 User login attempt:', credentials);` in `AuthContext.jsx`), which clutters the console and can leak sensitive data (like user credentials or access tokens) in production.
* **Hardcoded API Endpoints**: While `api.js` is used, some components still have hardcoded paths or complex query string concatenations that could be simplified with `axios` params.

---

## 3. IoT (ESP32 C++)

### Critical
* **String Memory Leaks**: The `esp32_ultrasonic.ino` file heavily uses Arduino `String` objects (e.g., `String payload = "{" + "\"device_id\":\"" + String(DEVICE_ID) + ...`). Concatenating Strings in a loop on the ESP32 can lead to heap fragmentation and eventually crash the device. It should use `snprintf` with fixed-size character arrays (`char buffer[256]`) instead.

### Functionality
* **No Validation for Maximum Weight**: The ESP32 code calculates `estimated_weight_kg = (fill_percentage / 100.0) * BIN_CAPACITY_KG;`. However, if the sensor misreads a negative distance or something very small, the fill percentage hits 100, but there's no way to know if the bin actually exceeds `BIN_CAPACITY_KG`.
* **Insecure HTTP Fallback**: The device blindly falls back to HTTP and uses `client->setInsecure()` for HTTPS, which skips SSL verification. This makes it vulnerable to Man-In-The-Middle (MITM) attacks. While noted as "fine for demo", this is a security risk for production.
* **Hardcoded Timeout/Delays**: Extensive use of `delay()` (e.g., `delay(WIFI_RETRY_DELAY_MS)`) makes the device completely unresponsive during those periods. If a reading comes in or state changes during the delay, it will be missed.

### Syntax/Improvement
* **Bubble Sort Inefficiency**: The `getFilteredDistance()` function uses a Bubble Sort algorithm for finding the median. While `NUM_SAMPLES` is small (5), it's generally better practice to use a more efficient sorting method or insertion sort.

---

## 4. Deployment Scripts & Config

### Functionality
* **Hardcoded Passwords in Compose File**: The `docker-compose.yml` provides fallback passwords (e.g., `POSTGRES_PASSWORD=${DB_PASSWORD:-secure_password_123}`). If `DB_PASSWORD` isn't set, it uses `secure_password_123`.
* **Resource Limits**: The `docker-compose.yml` sets strict memory limits (e.g., 256M for Postgres). Depending on the volume of IoT data, this might lead to Out Of Memory (OOM) crashes in production.
