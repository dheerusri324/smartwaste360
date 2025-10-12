# app.py (in root directory)

import os
import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS  # <-- 1. IMPORT CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-super-secret-key-for-dev')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'a-super-secret-jwt-key-for-dev')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'backend/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- INITIALIZE EXTENSIONS ---

# 👇 2. INITIALIZE CORS AND ALLOW YOUR REACT APP'S ORIGIN 👇
# Use Flask-CORS with explicit configuration
CORS(app, 
     origins=['*'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=False)

# Additional CORS handling for admin routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

jwt = JWTManager(app)

# --- CREATE DIRECTORIES ---
def create_directories():
    directories = ['backend/uploads', 'backend/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

create_directories()

# --- IMPORT & REGISTER BLUEPRINTS (ROUTES) ---
from routes import auth, waste, booking, leaderboard, camera, collector, transaction, health, colony, collection_points, admin, analytics

app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(waste.bp, url_prefix='/api/waste')
app.register_blueprint(booking.bp, url_prefix='/api/booking')
app.register_blueprint(leaderboard.bp, url_prefix='/api/leaderboard')
app.register_blueprint(camera.bp, url_prefix='/api/camera')
app.register_blueprint(collector.bp, url_prefix='/api/collector')
app.register_blueprint(transaction.bp, url_prefix='/api/transaction')
app.register_blueprint(colony.bp, url_prefix='/api/colony')
app.register_blueprint(collection_points.bp, url_prefix='/api/collection-points')
app.register_blueprint(admin.bp, url_prefix='/api/admin')
app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
app.register_blueprint(health.bp, url_prefix='/health')

# Advanced features temporarily disabled for debugging
# app.register_blueprint(advanced_features.bp, url_prefix='/api/advanced')

# --- ROOT ROUTE ---
@app.route('/')
def home():
    return jsonify({
        'message': 'SmartWaste360 API is alive! CORS v5.4.0',
        'version': '5.4.0',
        'status': 'production',
        'deployment': 'route-parameters-fixed',
        'timestamp': '2025-10-12',
        'cors_enabled': True,
        'cors_method': 'after_request_headers'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'cors_origins': 'all_origins_allowed',
        'timestamp': '2025-10-12',
        'version': '5.0.0'
    })

@app.route('/mobile-debug')
def mobile_debug():
    """Debug endpoint for mobile connectivity issues"""
    from flask import request
    return jsonify({
        'status': 'mobile_debug_success',
        'message': 'If you see this, DNS resolution is working!',
        'server': 'render',
        'timestamp': '2025-10-12',
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'origin': request.headers.get('Origin', 'No Origin'),
        'cors_enabled': True,
        'backend_url': 'https://smartwaste360-backend.onrender.com'
    })

@app.route('/debug-headers')
def debug_headers():
    """Debug all request headers"""
    from flask import request
    return jsonify({
        'status': 'debug_headers',
        'all_headers': dict(request.headers),
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'authorization_present': 'Authorization' in request.headers,
        'content_type': request.headers.get('Content-Type', 'Not set')
    })

@app.route('/test-collector-update/<collector_id>')
def test_collector_update(collector_id):
    """Test endpoint to verify route parameters are working"""
    return jsonify({
        'status': 'test_success',
        'message': 'Route parameters are working!',
        'collector_id_received': collector_id,
        'version': '5.4.0'
    })

@app.route('/create-test-user')
def create_test_user():
    """Create a test user for mobile testing"""
    try:
        import psycopg2
        import bcrypt
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create test user
        test_email = "test@smartwaste360.com"
        test_password = "test123"
        test_username = "testuser"
        
        # Hash password
        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert test user (ignore if exists)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, total_points)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING user_id;
        """, (test_username, test_email, password_hash, "Test User", 100))
        
        result = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Test user created/verified successfully!',
            'credentials': {
                'email': test_email,
                'password': test_password,
                'username': test_username
            },
            'user_created': result is not None,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Test user creation failed: {str(e)}',
            'status': 'failed'
        }), 500

@app.route('/add-missing-tables')
def add_missing_tables():
    """Add missing achievement and admin activity tables"""
    try:
        import psycopg2
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Add missing tables
        missing_tables_sql = """
        -- Achievement tables
        CREATE TABLE IF NOT EXISTS user_achievements (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
            achievement_id VARCHAR(50) NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points_awarded INT DEFAULT 0,
            UNIQUE(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS user_statistics (
            user_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
            waste_classifications INT DEFAULT 0,
            plastic_classifications INT DEFAULT 0,
            paper_classifications INT DEFAULT 0,
            metal_classifications INT DEFAULT 0,
            glass_classifications INT DEFAULT 0,
            organic_classifications INT DEFAULT 0,
            textile_classifications INT DEFAULT 0,
            total_weight_kg DECIMAL(10,2) DEFAULT 0,
            consecutive_days INT DEFAULT 0,
            last_classification_date DATE,
            colony_collections_triggered INT DEFAULT 0,
            current_colony_rank INT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Admin activity logs table
        CREATE TABLE IF NOT EXISTS admin_activity_logs (
            log_id SERIAL PRIMARY KEY,
            admin_id INT REFERENCES admins(admin_id),
            action VARCHAR(100) NOT NULL,
            target_type VARCHAR(50),
            target_id VARCHAR(50),
            details JSONB,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute the SQL
        cursor.execute(missing_tables_sql)
        conn.commit()
        
        # Verify all tables
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
            'message': 'Missing tables added successfully!',
            'tables_verified': table_names,
            'total_tables': len(table_names),
            'new_tables': ['user_achievements', 'user_statistics', 'admin_activity_logs'],
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Adding missing tables failed: {str(e)}',
            'status': 'failed'
        }), 500

@app.route('/setup-database')
def setup_database():
    """Setup database tables - run this once after deployment"""
    try:
        import psycopg2
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create tables with IF NOT EXISTS
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
            waste_types_accepted TEXT[], -- Array of waste types
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
        
        # Execute the SQL
        cursor.execute(setup_sql)
        conn.commit()
        
        # Verify tables were created
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

# --- RUN THE APP ---
if __name__ == '__main__':
    print("🚀 STARTING SMARTWASTE360 API v4.0.0 WITH CORS FIX")
    app.run(debug=True, host='0.0.0.0', port=5000)