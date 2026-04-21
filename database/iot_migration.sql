-- SmartWaste360 — IoT Sensor Readings Table
-- Run this migration to add IoT support to your database
-- 
-- Execute with: psql -d smartwaste360 -f database/iot_migration.sql
-- Or paste into your PostgreSQL client

-- Table to store all incoming sensor readings (time-series data)
CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    colony_id INT REFERENCES colonies(colony_id),
    waste_type VARCHAR(30) NOT NULL,
    fill_percentage DECIMAL(5,1) NOT NULL,
    estimated_weight_kg DECIMAL(10,2) NOT NULL,
    distance_cm DECIMAL(10,1),
    battery_level INT DEFAULT 100,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast colony + time queries (dashboard/charts)
CREATE INDEX IF NOT EXISTS idx_sensor_colony_time 
    ON sensor_readings(colony_id, recorded_at DESC);

-- Index for fast device lookups
CREATE INDEX IF NOT EXISTS idx_sensor_device 
    ON sensor_readings(device_id, recorded_at DESC);

-- Verify:
-- SELECT * FROM sensor_readings LIMIT 5;
