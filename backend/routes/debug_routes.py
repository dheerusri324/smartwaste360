# backend/routes/debug_routes.py
"""
Debug and diagnostic endpoints — only registered when FLASK_DEBUG is enabled.
These endpoints expose internal database state and should NEVER be available in production.
"""

import os
from flask import Blueprint, request, jsonify

bp = Blueprint('debug_routes', __name__)


@bp.route('/test-collectors')
def test_collectors():
    """Test endpoint to verify collectors query works"""
    try:
        from models.collector import Collector
        collectors = Collector.get_all_collectors()
        return jsonify({
            'status': 'success',
            'collectors_count': len(collectors),
            'message': 'Collectors query working!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Collectors query failed'
        }), 500


@bp.route('/debug-database')
def debug_database():
    """Debug endpoint to check database contents"""
    try:
        from config.database import get_db
        from psycopg2.extras import RealDictCursor

        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users")
                users_count = cursor.fetchone()['count']

                cursor.execute("SELECT COUNT(*) as count FROM collectors")
                collectors_count = cursor.fetchone()['count']

                cursor.execute("SELECT COUNT(*) as count FROM admins")
                admins_count = cursor.fetchone()['count']

                cursor.execute("""
                    SELECT COUNT(*) as count FROM users 
                    WHERE created_at > NOW() - INTERVAL '7 days'
                """)
                recent_users = cursor.fetchone()['count']

                return jsonify({
                    'status': 'success',
                    'database_stats': {
                        'total_users': users_count,
                        'total_collectors': collectors_count,
                        'total_admins': admins_count,
                        'recent_users_7_days': recent_users
                    },
                    'message': 'Database accessible'
                })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Database query failed'
        }), 500


@bp.route('/debug-colonies')
def debug_colonies():
    """Debug endpoint to check colonies table structure"""
    try:
        from config.database import get_db
        from psycopg2.extras import RealDictCursor

        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'colonies'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()

                cursor.execute("SELECT * FROM colonies LIMIT 3")
                colonies = cursor.fetchall()

                return jsonify({
                    'status': 'success',
                    'table_structure': [dict(c) for c in columns],
                    'colonies_count': len(colonies),
                    'sample_colonies': [dict(c) for c in colonies]
                })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/debug-collectors')
def debug_collectors():
    """Debug endpoint to check collectors table"""
    try:
        from config.database import get_db
        from psycopg2.extras import RealDictCursor

        with get_db() as db:
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'collectors'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()

                cursor.execute("SELECT * FROM collectors LIMIT 3")
                collectors = cursor.fetchall()

                return jsonify({
                    'status': 'success',
                    'table_structure': [dict(c) for c in columns],
                    'collectors_count': len(collectors),
                    'sample_collectors': [dict(c) for c in collectors]
                })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/fix-colonies-table')
def fix_colonies_table():
    """Fix colonies table by adding missing waste tracking columns"""
    try:
        from config.database import get_db

        with get_db() as db:
            with db.cursor() as cursor:
                waste_columns = [
                    "current_plastic_kg DECIMAL(10,2) DEFAULT 0",
                    "current_paper_kg DECIMAL(10,2) DEFAULT 0",
                    "current_metal_kg DECIMAL(10,2) DEFAULT 0",
                    "current_glass_kg DECIMAL(10,2) DEFAULT 0",
                    "current_textile_kg DECIMAL(10,2) DEFAULT 0",
                    "current_dry_waste_kg DECIMAL(10,2) DEFAULT 0",
                    "last_collection_date TIMESTAMP",
                    "collection_frequency_days INTEGER DEFAULT 7"
                ]

                for column in waste_columns:
                    cursor.execute(f"""
                        ALTER TABLE colonies 
                        ADD COLUMN IF NOT EXISTS {column}
                    """)

                booking_columns = [
                    "total_weight DECIMAL(10,2) DEFAULT 0",
                    "notes TEXT",
                    "waste_types_collected TEXT"
                ]

                for column in booking_columns:
                    cursor.execute(f"""
                        ALTER TABLE collection_bookings 
                        ADD COLUMN IF NOT EXISTS {column}
                    """)

                cursor.execute("""
                    UPDATE colonies 
                    SET current_plastic_kg = 6.5,
                        current_paper_kg = 8.2,
                        current_metal_kg = 1.5,
                        current_glass_kg = 3.0,
                        current_textile_kg = 2.1,
                        current_dry_waste_kg = 12.5
                    WHERE colony_id = 1
                """)

                db.commit()

                return jsonify({
                    'status': 'success',
                    'message': 'Colonies and collection_bookings tables structure fixed'
                })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/fix-collectors-table')
def fix_collectors_table():
    """Fix collectors table by adding missing columns"""
    try:
        from config.database import get_db

        with get_db() as db:
            with db.cursor() as cursor:
                cursor.execute("""
                    ALTER TABLE collectors 
                    ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
                """)
                cursor.execute("""
                    ALTER TABLE collectors 
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                cursor.execute("""
                    ALTER TABLE collectors 
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
                """)
                cursor.execute("""
                    ALTER TABLE collectors 
                    ADD COLUMN IF NOT EXISTS total_weight_collected DECIMAL(10,2) DEFAULT 0
                """)
                db.commit()

                return jsonify({
                    'status': 'success',
                    'message': 'Collectors table structure fixed with all required columns'
                })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/mobile-debug')
def mobile_debug():
    """Debug endpoint for mobile connectivity issues"""
    return jsonify({
        'status': 'mobile_debug_success',
        'message': 'If you see this, DNS resolution is working!',
        'server': 'render',
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'origin': request.headers.get('Origin', 'No Origin'),
        'cors_enabled': True,
        'backend_url': 'https://smartwaste360-backend.onrender.com'
    })


@bp.route('/debug-headers')
def debug_headers():
    """Debug all request headers"""
    return jsonify({
        'status': 'debug_headers',
        'all_headers': dict(request.headers),
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'authorization_present': 'Authorization' in request.headers,
        'content_type': request.headers.get('Content-Type', 'Not set')
    })


@bp.route('/test-collector-update/<collector_id>')
def test_collector_update(collector_id):
    """Test endpoint to verify route parameters are working"""
    return jsonify({
        'status': 'test_success',
        'message': 'Route parameters are working!',
        'collector_id_received': collector_id
    })


@bp.route('/create-test-user')
def create_test_user():
    """Create a test user for mobile testing"""
    try:
        import psycopg2
        import bcrypt

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        test_email = "test@smartwaste360.com"
        test_password = "test123"
        test_username = "testuser"

        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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


@bp.route('/add-missing-tables')
def add_missing_tables():
    """Add missing achievement and admin activity tables"""
    try:
        import psycopg2

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        missing_tables_sql = """
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

        cursor.execute(missing_tables_sql)
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
