# backend/models/admin.py

from config.database import get_db
import bcrypt
from psycopg2.extras import RealDictCursor

class Admin:
    @staticmethod
    def create_admin(username, email, password, full_name, role='admin'):
        """Create a new admin user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = """
            INSERT INTO admins (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING admin_id
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (username, email, password_hash, full_name, role))
                admin_id = cursor.fetchone()['admin_id']
                db.commit()
                return admin_id

    @staticmethod
    def get_by_email(email):
        """Get admin by email"""
        sql = "SELECT * FROM admins WHERE email = %s AND is_active = TRUE"
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (email,))
                return cursor.fetchone()

    @staticmethod
    def get_by_username(username):
        """Get admin by username"""
        sql = "SELECT * FROM admins WHERE username = %s AND is_active = TRUE"
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (username,))
                return cursor.fetchone()

    @staticmethod
    def get_by_id(admin_id):
        """Get admin by ID"""
        sql = "SELECT * FROM admins WHERE admin_id = %s AND is_active = TRUE"
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (admin_id,))
                return cursor.fetchone()

    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify admin password"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

    @staticmethod
    def get_system_overview():
        """Get comprehensive system overview for admin dashboard"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get overall statistics
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as total_users,
                        (SELECT COUNT(*) FROM collectors WHERE is_active = TRUE) as total_collectors,
                        (SELECT COUNT(*) FROM colonies) as total_colonies,
                        (SELECT COUNT(*) FROM collection_points WHERE is_active = TRUE) as total_collection_points,
                        (SELECT COUNT(*) FROM waste_logs) as total_waste_classifications,
                        (SELECT COALESCE(SUM(weight_kg), 0) FROM waste_logs) as total_waste_processed,
                        (SELECT COALESCE(SUM(points_earned), 0) FROM waste_logs) as total_points_awarded,
                        (SELECT COALESCE(SUM(co2_saved), 0) FROM waste_logs) as total_co2_saved,
                        (SELECT COUNT(*) FROM collection_bookings WHERE status = 'completed') as total_collections_completed,
                        (SELECT COALESCE(SUM(total_weight_collected), 0) FROM collection_bookings WHERE status = 'completed') as total_weight_collected
                """)
                overview = cursor.fetchone()
                
                # Get recent activity
                cursor.execute("""
                    SELECT 'waste_classification' as activity_type, 
                           u.username, wl.predicted_category, wl.weight_kg, wl.created_at
                    FROM waste_logs wl
                    JOIN users u ON wl.user_id = u.user_id
                    ORDER BY wl.created_at DESC
                    LIMIT 10
                """)
                recent_activity = cursor.fetchall()
                
                # Get top performing colonies
                cursor.execute("""
                    SELECT colony_name, total_points, total_users,
                           COALESCE(SUM(wl.weight_kg), 0) as total_waste_generated
                    FROM colonies c
                    LEFT JOIN users u ON c.colony_id = u.colony_id
                    LEFT JOIN waste_logs wl ON u.user_id = wl.user_id
                    GROUP BY c.colony_id, c.colony_name, c.total_points, c.total_users
                    ORDER BY c.total_points DESC
                    LIMIT 10
                """)
                top_colonies = cursor.fetchall()
                
                # Get waste type breakdown
                cursor.execute("""
                    SELECT predicted_category, 
                           COUNT(*) as count,
                           COALESCE(SUM(weight_kg), 0) as total_weight,
                           COALESCE(SUM(points_earned), 0) as total_points
                    FROM waste_logs
                    GROUP BY predicted_category
                    ORDER BY total_weight DESC
                """)
                waste_breakdown = cursor.fetchall()
                
                return {
                    'overview': overview,
                    'recent_activity': recent_activity,
                    'top_colonies': top_colonies,
                    'waste_breakdown': waste_breakdown
                }

    @staticmethod
    def get_analytics_data(date_range='30d'):
        """Get detailed analytics data for admin dashboard"""
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Date range calculation
                if date_range == '7d':
                    date_filter = "created_at >= NOW() - INTERVAL '7 days'"
                elif date_range == '30d':
                    date_filter = "created_at >= NOW() - INTERVAL '30 days'"
                elif date_range == '90d':
                    date_filter = "created_at >= NOW() - INTERVAL '90 days'"
                else:
                    date_filter = "created_at >= NOW() - INTERVAL '30 days'"
                
                # Daily waste classification trends
                cursor.execute(f"""
                    SELECT DATE(created_at) as date,
                           COUNT(*) as classifications,
                           COALESCE(SUM(weight_kg), 0) as total_weight,
                           COALESCE(SUM(points_earned), 0) as total_points
                    FROM waste_logs
                    WHERE {date_filter}
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                daily_trends = cursor.fetchall()
                
                # User engagement metrics
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT user_id) as active_users,
                           AVG(daily_classifications) as avg_classifications_per_user
                    FROM (
                        SELECT user_id, DATE(created_at) as date, COUNT(*) as daily_classifications
                        FROM waste_logs
                        WHERE {date_filter}
                        GROUP BY user_id, DATE(created_at)
                    ) daily_user_stats
                """)
                engagement_metrics = cursor.fetchone()
                
                # Collection efficiency
                cursor.execute(f"""
                    SELECT COUNT(*) as total_bookings,
                           COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_bookings,
                           AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) as avg_completion_time_hours
                    FROM collection_bookings
                    WHERE {date_filter}
                """)
                collection_efficiency = cursor.fetchone()
                
                return {
                    'daily_trends': daily_trends,
                    'engagement_metrics': engagement_metrics,
                    'collection_efficiency': collection_efficiency
                }