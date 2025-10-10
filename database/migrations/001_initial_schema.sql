-- Migration 001: Initial Schema Setup
-- This migration creates the complete database schema for Smart Waste 360

-- Create custom types
CREATE TYPE waste_type_enum AS ENUM ('dry', 'wet');
CREATE TYPE status_enum AS ENUM ('scheduled', 'completed', 'cancelled');
CREATE TYPE notification_type_enum AS ENUM ('collection', 'points', 'achievement', 'system');

-- 1. Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(15),
    colony_id INT,
    total_points INT DEFAULT 0,
    total_weight_recycled DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Colonies table
CREATE TABLE colonies (
    colony_id SERIAL PRIMARY KEY,
    colony_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    total_points INT DEFAULT 0,
    total_users INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Waste logs table
CREATE TABLE waste_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT,
    image_path VARCHAR(255),
    predicted_category VARCHAR(50),
    confidence DECIMAL(5,2),
    weight_kg DECIMAL(10,2),
    waste_type waste_type_enum,
    points_earned INT,
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),
    is_recyclable BOOLEAN,
    co2_saved DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Collectors table
CREATE TABLE collectors (
    collector_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    assigned_colonies TEXT,
    vehicle_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Collection bookings table
CREATE TABLE collection_bookings (
    booking_id SERIAL PRIMARY KEY,
    colony_id INT,
    collector_id VARCHAR(20),
    booking_date DATE,
    time_slot VARCHAR(20),
    status status_enum DEFAULT 'scheduled',
    total_weight_collected DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (colony_id) REFERENCES colonies(colony_id) ON DELETE CASCADE,
    FOREIGN KEY (collector_id) REFERENCES collectors(collector_id) ON DELETE CASCADE
);

-- 6. User transactions table
CREATE TABLE user_transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT,
    booking_id INT,
    collector_id VARCHAR(20),
    weight_deposited DECIMAL(10,2),
    points_earned INT,
    materials JSONB,
    verification_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES collection_bookings(booking_id) ON DELETE CASCADE
);

-- 7. Notifications table
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT,
    title VARCHAR(200),
    message TEXT,
    type notification_type_enum,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 8. Points configuration table
CREATE TABLE points_config (
    material_type VARCHAR(50) PRIMARY KEY,
    points_per_kg INT,
    is_recyclable BOOLEAN,
    co2_factor DECIMAL(5,2)
);

-- Insert default points configuration
INSERT INTO points_config (material_type, points_per_kg, is_recyclable, co2_factor) VALUES 
('organic', 15, FALSE, 0.5),
('paper', 20, TRUE, 1.5),
('plastic', 25, TRUE, 2.5),
('glass', 20, TRUE, 1.0),
('metal', 30, TRUE, 1.0),
('textile', 20, TRUE, 2.0),
('others', 5, FALSE, 0.0);

-- Create indexes for better performance
CREATE INDEX idx_user_colony ON users(colony_id);
CREATE INDEX idx_waste_user ON waste_logs(user_id);
CREATE INDEX idx_booking_colony ON collection_bookings(colony_id);
CREATE INDEX idx_notification_user ON notifications(user_id);

-- Migration completed