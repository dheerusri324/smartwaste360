-- Migration 002: Add Notification Functions and Views
-- This migration adds additional database functions and views

-- Create a function to update colony points when user points change
CREATE OR REPLACE FUNCTION update_colony_points()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE colonies 
        SET total_points = total_points + NEW.points_earned
        FROM users
        WHERE colonies.colony_id = users.colony_id AND users.user_id = NEW.user_id;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE colonies 
        SET total_points = total_points + (NEW.points_earned - OLD.points_earned)
        FROM users
        WHERE colonies.colony_id = users.colony_id AND users.user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to update colony points when waste logs are inserted/updated
CREATE TRIGGER waste_log_points_trigger
    AFTER INSERT OR UPDATE OF points_earned ON waste_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_colony_points();

-- Create a function to update colony user count
CREATE OR REPLACE FUNCTION update_colony_user_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE colonies SET total_users = total_users + 1 WHERE colony_id = NEW.colony_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.colony_id IS DISTINCT FROM NEW.colony_id THEN
        UPDATE colonies SET total_users = total_users - 1 WHERE colony_id = OLD.colony_id;
        UPDATE colonies SET total_users = total_users + 1 WHERE colony_id = NEW.colony_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE colonies SET total_users = total_users - 1 WHERE colony_id = OLD.colony_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to update colony user count
CREATE TRIGGER user_colony_trigger
    AFTER INSERT OR UPDATE OF colony_id OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_colony_user_count();

-- Create a view for colony leaderboard
CREATE VIEW colony_leaderboard AS
SELECT 
    colony_id,
    colony_name,
    total_points,
    total_users,
    RANK() OVER (ORDER BY total_points DESC) as rank
FROM colonies
ORDER BY total_points DESC;

-- Create a view for user leaderboard within colonies
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

-- Add additional indexes for better performance
CREATE INDEX idx_collector_active ON collectors(is_active);
CREATE INDEX idx_booking_status ON collection_bookings(status);
CREATE INDEX idx_booking_date ON collection_bookings(booking_date);

-- Migration completed