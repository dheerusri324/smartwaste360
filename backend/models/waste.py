# backend/models/waste.py

from config.database import get_db
from psycopg2.extras import RealDictCursor

class WasteLog:
    @staticmethod
    def create_waste_log(user_id, image_path, predicted_category, confidence,
                         weight_kg, waste_type, points_earned, location_lat,
                         location_lng, is_recyclable, co2_saved):
        """Create a new waste classification log"""
        sql = """
            INSERT INTO waste_logs 
            (user_id, image_path, predicted_category, confidence, weight_kg, 
             waste_type, points_earned, location_lat, location_lng, is_recyclable, co2_saved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING log_id
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (
                    user_id, image_path, predicted_category, confidence, weight_kg,
                    waste_type, points_earned, location_lat, location_lng, is_recyclable, co2_saved
                ))
                log_id = cursor.fetchone()['log_id']
                db.commit()
                return log_id

    @staticmethod
    def get_user_waste_logs(user_id, page=1, limit=10):
        """Gets a paginated list of waste logs for a specific user."""
        offset = (page - 1) * limit
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                # --- THIS IS THE FIX ---
                # Before: SELECT COUNT(*) as total ... and then reading 'count'
                # After: We correctly alias as 'total' and read 'total'.
                cursor.execute("SELECT COUNT(*) as total FROM waste_logs WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                total = result['total'] if result else 0
                
                sql = """
                    SELECT * FROM waste_logs
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (user_id, limit, offset))
                logs = cursor.fetchall()
                
                return {
                    "logs": logs,
                    "total": total,
                    "page": page,
                    "total_pages": (total + limit - 1) // limit
                }

    @staticmethod
    def get_waste_stats(user_id):
        """Gets waste statistics for a user."""
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                sql_overall = """
                    SELECT
                        COALESCE(COUNT(*), 0) as total_scans,
                        COALESCE(SUM(weight_kg), 0.0) as total_weight,
                        COALESCE(SUM(points_earned), 0) as total_points,
                        COALESCE(SUM(co2_saved), 0.0) as total_co2_saved,
                        COALESCE(SUM(CASE WHEN is_recyclable THEN weight_kg ELSE 0 END), 0.0) as recyclable_weight
                    FROM waste_logs
                    WHERE user_id = %s
                """
                cursor.execute(sql_overall, (user_id,))
                overall_stats = cursor.fetchone()
                
                sql_category = """
                    SELECT
                        predicted_category, COUNT(*) as count, SUM(weight_kg) as total_weight, SUM(points_earned) as total_points
                    FROM waste_logs
                    WHERE user_id = %s
                    GROUP BY predicted_category
                """
                cursor.execute(sql_category, (user_id,))
                category_stats = cursor.fetchall()
                
                return {
                    "overall": overall_stats,
                    "by_category": category_stats
                }