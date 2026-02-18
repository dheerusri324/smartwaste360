-- Smart Waste 360 - Neon Database Setup
-- Run this in Neon SQL Editor

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
    current_plastic_kg DECIMAL(10,2) DEFAULT 0.00,
    current_paper_kg DECIMAL(10,2) DEFAULT 0.00,
    current_metal_kg DECIMAL(10,2) DEFAULT 0.00,
    current_glass_kg DECIMAL(10,2) DEFAULT 0.00,
    current_textile_kg DECIMAL(10,2) DEFAULT 0.00,
    current_dry_waste_kg DECIMAL(10,2) DEFAULT 0.00,
    last_collection_date TIMESTAMP,
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
    password_hash VARCHAR(255),
    assigned_colonies TEXT,
    vehicle_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    total_weight_collected DECIMAL(10,2) DEFAULT 0.00,
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

-- 9. Admins table
CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 10. Collection points table
CREATE TABLE collection_points (
    point_id SERIAL PRIMARY KEY,
    colony_id INT,
    point_name VARCHAR(100) NOT NULL,
    location_description TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    waste_types_accepted TEXT[],
    max_capacity_kg DECIMAL(10,2) DEFAULT 100.00,
    current_capacity_kg DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_collection_date DATE,
    FOREIGN KEY (colony_id) REFERENCES colonies(colony_id) ON DELETE CASCADE
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

-- Insert default admin (password: admin)
INSERT INTO admins (username, email, password_hash, full_name) VALUES 
('admin', 'admin@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ632u', 'System Administrator');

-- Insert test collectors
INSERT INTO collectors (collector_id, name, phone, email, assigned_colonies, vehicle_number, is_active) VALUES 
('COL001', 'John Collector', '9876543210', 'john@collector.com', 'Colony A, Colony B', 'AP01AB1234', TRUE),
('COL002', 'Jane Collector', '9876543211', 'jane@collector.com', 'Colony C, Colony D', 'AP01AB5678', TRUE),
('COL003', 'Mike Collector', '9876543212', 'mike@collector.com', 'Colony E, Colony F', 'AP01AB9012', FALSE);

-- Insert test colonies with waste
INSERT INTO colonies (colony_name, address, city, state, pincode, latitude, longitude, current_plastic_kg, current_paper_kg, current_metal_kg) VALUES
('Test Colony A', '123 Main St', 'Hyderabad', 'Telangana', '500001', 17.385044, 78.486671, 15.5, 10.2, 5.3),
('Test Colony B', '456 Park Ave', 'Hyderabad', 'Telangana', '500002', 17.445240, 78.348915, 20.0, 15.5, 8.0)
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX idx_user_colony ON users(colony_id);
CREATE INDEX idx_waste_user ON waste_logs(user_id);
CREATE INDEX idx_booking_colony ON collection_bookings(colony_id);
CREATE INDEX idx_notification_user ON notifications(user_id);
CREATE INDEX idx_collector_active ON collectors(is_active);
CREATE INDEX idx_booking_status ON collection_bookings(status);
CREATE INDEX idx_booking_date ON collection_bookings(booking_date);
CREATE INDEX idx_collector_email ON collectors(email);
CREATE INDEX idx_collection_points_colony ON collection_points(colony_id);

-- Create views for leaderboards
CREATE VIEW colony_leaderboard AS
SELECT 
    colony_id,
    colony_name,
    total_points,
    total_users,
    RANK() OVER (ORDER BY total_points DESC) as rank
FROM colonies
ORDER BY total_points DESC;

CREATE VIEW user_leaderboard AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.colony_id,
    c.colony_name,
    u.total_points,
    u.total_weight_recycled,
    RANK() OVER (PARTITION BY u.colony_id ORDER BY u.total_points DESC) as colony_rank,
    RANK() OVER (ORDER BY u.total_points DESC) as global_rank
FROM users u
JOIN colonies c ON u.colony_id = c.colony_id
WHERE u.is_active = TRUE
ORDER BY u.total_points DESC;
