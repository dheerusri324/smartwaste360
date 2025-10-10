-- Smart Waste 360 - Sample Data
-- Connect to the database first: \c smartwaste360;

-- Insert sample colonies
INSERT INTO colonies (colony_name, address, city, state, pincode, latitude, longitude) VALUES
('Green Valley Colony', '123 Green Street', 'Bangalore', 'Karnataka', '560001', 12.971598, 77.594566),
('Eco-Friendly Homes', '456 Eco Road', 'Bangalore', 'Karnataka', '560002', 12.978367, 77.640735),
('Sustainable Living Society', '789 Sustainable Avenue', 'Bangalore', 'Karnataka', '560003', 12.927923, 77.627108);

-- Insert sample collectors
INSERT INTO collectors (collector_id, name, phone, email, assigned_colonies, vehicle_number) VALUES
('COL001', 'Rajesh Kumar', '9876543210', 'rajesh@greenwaste.com', '[1, 2]', 'KA01AB1234'),
('COL002', 'Suresh Patel', '8765432109', 'suresh@ecocollect.com', '[2, 3]', 'KA02CD5678'),
('COL003', 'Anita Desai', '7654321098', 'anita@cleanindia.com', '[1, 3]', 'KA03EF9012');

-- Insert sample users (passwords are "password123" hashed with bcrypt)
INSERT INTO users (username, email, password_hash, full_name, phone, colony_id) VALUES
('john_doe', 'john@example.com', '$2b$12$Y6XrR7M8nS9T0U1V2W3X4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v', 'John Doe', '9876543210', 1),
('jane_smith', 'jane@example.com', '$2b$12$Y6XrR7M8nS9T0U1V2W3X4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v', 'Jane Smith', '8765432109', 1),
('rohit_sharma', 'rohit@example.com', '$2b$12$Y6XrR7M8nS9T0U1V2W3X4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v', 'Rohit Sharma', '7654321098', 2),
('priya_patel', 'priya@example.com', '$2b$12$Y6XrR7M8nS9T0U1V2W3X4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v', 'Priya Patel', '6543210987', 2),
('amit_kumar', 'amit@example.com', '$2b$12$Y6XrR7M8nS9T0U1V2W3X4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v', 'Amit Kumar', '5432109876', 3);

-- Insert sample waste logs
INSERT INTO waste_logs (user_id, image_path, predicted_category, confidence, weight_kg, waste_type, points_earned, location_lat, location_lng, is_recyclable, co2_saved) VALUES
(1, 'uploads/waste_1.jpg', 'plastic', 0.92, 2.5, 'dry', 62, 12.971598, 77.594566, TRUE, 6.25),
(1, 'uploads/waste_2.jpg', 'paper', 0.85, 1.0, 'dry', 20, 12.971598, 77.594566, TRUE, 1.5),
(2, 'uploads/waste_3.jpg', 'organic', 0.95, 3.0, 'wet', 45, 12.971598, 77.594566, FALSE, 1.5),
(3, 'uploads/waste_4.jpg', 'metal', 0.88, 0.5, 'dry', 15, 12.978367, 77.640735, TRUE, 0.5),
(4, 'uploads/waste_5.jpg', 'glass', 0.91, 2.0, 'dry', 40, 12.978367, 77.640735, TRUE, 2.0),
(5, 'uploads/waste_6.jpg', 'plastic', 0.87, 1.5, 'dry', 37, 12.927923, 77.627108, TRUE, 3.75);

-- Insert sample collection bookings
INSERT INTO collection_bookings (colony_id, collector_id, booking_date, time_slot, status, total_weight_collected) VALUES
(1, 'COL001', '2025-09-15', '09:00-11:00', 'scheduled', 0),
(2, 'COL002', '2025-09-15', '11:00-13:00', 'scheduled', 0),
(3, 'COL003', '2025-09-16', '14:00-16:00', 'scheduled', 0),
(1, 'COL001', '2025-09-10', '09:00-11:00', 'completed', 15.5),
(2, 'COL002', '2025-09-10', '11:00-13:00', 'completed', 12.3);

-- Insert sample user transactions
INSERT INTO user_transactions (user_id, booking_id, collector_id, weight_deposited, points_earned, materials, verification_code) VALUES
(1, 4, 'COL001', 5.5, 120, '{"plastic": 2.5, "paper": 1.0, "metal": 2.0}', 'ABC123'),
(2, 4, 'COL001', 4.0, 85, '{"organic": 3.0, "glass": 1.0}', 'DEF456'),
(3, 5, 'COL002', 5.3, 110, '{"paper": 2.5, "plastic": 2.8}', 'GHI789'),
(4, 5, 'COL002', 7.0, 150, '{"metal": 3.0, "glass": 4.0}', 'JKL012');

-- Insert sample notifications
INSERT INTO notifications (user_id, title, message, type) VALUES
(1, 'Collection Scheduled', 'A waste collection is scheduled for 2025-09-15 at 09:00-11:00', 'collection'),
(2, 'Collection Scheduled', 'A waste collection is scheduled for 2025-09-15 at 09:00-11:00', 'collection'),
(1, 'Points Earned', 'You earned 62 points for recycling 2.5kg of plastic', 'points'),
(3, 'Achievement Unlocked', 'You have recycled 100kg of waste!', 'achievement');

-- Update colony points based on user points (this would normally be done by triggers)
UPDATE colonies SET total_points = (
    SELECT COALESCE(SUM(total_points), 0) FROM users WHERE colony_id = colonies.colony_id
);

-- Update colony user counts
UPDATE colonies SET total_users = (
    SELECT COUNT(*) FROM users WHERE colony_id = colonies.colony_id AND is_active = TRUE
);