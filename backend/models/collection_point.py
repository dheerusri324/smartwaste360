# backend/models/collection_point.py

from config.database import get_db
from psycopg2.extras import RealDictCursor

class CollectionPoint:
    @staticmethod
    def get_by_colony(colony_id):
        """Get all collection points for a specific colony."""
        sql = """
            SELECT * FROM collection_points 
            WHERE colony_id = %s AND is_active = TRUE
            ORDER BY point_name
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (colony_id,))
                return cursor.fetchall()

    @staticmethod
    def get_all_active():
        """Get all active collection points with colony information."""
        sql = """
            SELECT cp.*, c.colony_name, c.address as colony_address
            FROM collection_points cp
            JOIN colonies c ON cp.colony_id = c.colony_id
            WHERE cp.is_active = TRUE
            ORDER BY c.colony_name, cp.point_name
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

    @staticmethod
    def get_by_waste_type(waste_types):
        """Get collection points that accept specific waste types."""
        if not waste_types:
            return CollectionPoint.get_all_active()
            
        sql = """
            SELECT cp.*, c.colony_name, c.address as colony_address
            FROM collection_points cp
            JOIN colonies c ON cp.colony_id = c.colony_id
            WHERE cp.is_active = TRUE 
            AND cp.waste_types_accepted && %s
            ORDER BY c.colony_name, cp.point_name
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (waste_types,))
                return cursor.fetchall()

    @staticmethod
    def create(colony_id, point_name, location_description, latitude, longitude, 
               waste_types_accepted, max_capacity_kg=100.00):
        """Create a new collection point."""
        sql = """
            INSERT INTO collection_points 
            (colony_id, point_name, location_description, latitude, longitude, 
             waste_types_accepted, max_capacity_kg)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING point_id
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (
                    colony_id, point_name, location_description, latitude, longitude,
                    waste_types_accepted, max_capacity_kg
                ))
                point_id = cursor.fetchone()['point_id']
                db.commit()
                return point_id

    @staticmethod
    def update_capacity(point_id, weight_collected):
        """Update collection point capacity after collection."""
        sql = """
            UPDATE collection_points 
            SET current_capacity_kg = GREATEST(0, current_capacity_kg - %s),
                last_collection_date = CURRENT_DATE
            WHERE point_id = %s
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (weight_collected, point_id))
                db.commit()

    @staticmethod
    def get_nearby(latitude, longitude, radius_km=5):
        """Get collection points within a certain radius."""
        sql = """
            SELECT *
            FROM (
                SELECT cp.*, c.colony_name, c.address as colony_address,
                    (6371 * acos(
                        LEAST(1.0, 
                            cos(radians(%s)) * cos(radians(CAST(cp.latitude AS FLOAT))) * 
                            cos(radians(CAST(cp.longitude AS FLOAT)) - radians(%s)) + 
                            sin(radians(%s)) * sin(radians(CAST(cp.latitude AS FLOAT)))
                        )
                    )) AS distance
                FROM collection_points cp
                JOIN colonies c ON cp.colony_id = c.colony_id
                WHERE cp.is_active = TRUE
                    AND cp.latitude IS NOT NULL 
                    AND cp.longitude IS NOT NULL
            ) AS points_with_distance
            WHERE distance <= %s
            ORDER BY distance
        """
        with get_db() as db:
            if not db: 
                raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (latitude, longitude, latitude, radius_km))
                return cursor.fetchall()