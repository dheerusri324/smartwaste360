# backend/routes/setup.py
"""
Database setup endpoint — only registered when FLASK_DEBUG is enabled.
Run once after initial deployment to create all tables and seed data.
"""

import os
from flask import Blueprint, jsonify

bp = Blueprint('setup', __name__)


@bp.route('/setup-database')
def setup_database():
    """Setup database tables - run this once after deployment"""
    try:
        import psycopg2

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        setup_sql = """
        -- Create custom types (with IF NOT EXISTS equivalent)
        DO $$ BEGIN
            CREATE TYPE waste_type_enum AS ENUM ('dry', 'wet');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE status_enum AS ENUM ('scheduled', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE notification_type_enum AS ENUM ('collection', 'points', 'achievement', 'system');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;

        -- Create tables with IF NOT EXISTS
        CREATE TABLE IF NOT EXISTS users (
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

        CREATE TABLE IF NOT EXISTS colonies (
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

        CREATE TABLE IF NOT EXISTS waste_logs (
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

        CREATE TABLE IF NOT EXISTS collectors (
            collector_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            email VARCHAR(100),
            assigned_colonies TEXT,
            vehicle_number VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS collection_bookings (
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

        CREATE TABLE IF NOT EXISTS user_transactions (
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

        CREATE TABLE IF NOT EXISTS notifications (
            notification_id SERIAL PRIMARY KEY,
            user_id INT,
            title VARCHAR(200),
            message TEXT,
            type notification_type_enum,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS points_config (
            material_type VARCHAR(50) PRIMARY KEY,
            points_per_kg INT,
            is_recyclable BOOLEAN,
            co2_factor DECIMAL(5,2)
        );

        -- Admin table
        CREATE TABLE IF NOT EXISTS admins (
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

        -- Collection Points table
        CREATE TABLE IF NOT EXISTS collection_points (
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

        -- Insert default points configuration (only if empty)
        INSERT INTO points_config (material_type, points_per_kg, is_recyclable, co2_factor) 
        SELECT * FROM (VALUES 
            ('organic', 15, FALSE, 0.5),
            ('paper', 20, TRUE, 1.5),
            ('plastic', 25, TRUE, 2.5),
            ('glass', 20, TRUE, 1.0),
            ('metal', 30, TRUE, 1.0),
            ('textile', 20, TRUE, 2.0),
            ('others', 5, FALSE, 0.0)
        ) AS v(material_type, points_per_kg, is_recyclable, co2_factor)
        WHERE NOT EXISTS (SELECT 1 FROM points_config WHERE points_config.material_type = v.material_type);

        -- Insert test collectors (only if empty)
        INSERT INTO collectors (collector_id, name, phone, email, assigned_colonies, vehicle_number, is_active)
        SELECT * FROM (VALUES 
            ('COL001', 'John Collector', '9876543210', 'john@collector.com', 'Colony A, Colony B', 'AP01AB1234', TRUE),
            ('COL002', 'Jane Collector', '9876543211', 'jane@collector.com', 'Colony C, Colony D', 'AP01AB5678', TRUE),
            ('COL003', 'Mike Collector', '9876543212', 'mike@collector.com', 'Colony E, Colony F', 'AP01AB9012', FALSE)
        ) AS c(collector_id, name, phone, email, assigned_colonies, vehicle_number, is_active)
        WHERE NOT EXISTS (SELECT 1 FROM collectors WHERE collectors.collector_id = c.collector_id);
        """

        cursor.execute(setup_sql)
        conn.commit()

        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        cursor.close()
        conn.close()

        return jsonify({
            'message': 'Database setup completed successfully!',
            'tables_verified': table_names,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': f'Database setup failed: {str(e)}',
            'status': 'failed'
        }), 500
