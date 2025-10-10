# backend/models/collector.py

from config.database import get_db
import bcrypt
from psycopg2.extras import RealDictCursor

class Collector:
    @staticmethod
    def create(name, phone, email, password, vehicle_number=None):
        """Creates a new collector with a hashed password."""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = """
            INSERT INTO collectors (name, phone, email, password_hash, vehicle_number)
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING collector_id
        """
        params = (name, phone, email, password_hash, vehicle_number)
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                new_collector = cursor.fetchone()
                db.commit()
                return new_collector['collector_id']

    @staticmethod
    def get_by_id(collector_id):
        """Gets a single collector by their ID."""
        sql = "SELECT * FROM collectors WHERE collector_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (collector_id,))
                return cursor.fetchone()

    @staticmethod
    def get_by_email(email):
        """Gets a single collector by their email address."""
        sql = "SELECT * FROM collectors WHERE email = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (email,))
                return cursor.fetchone()

    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verifies a provided password against a stored hash."""
        if stored_hash is None or provided_password is None:
            return False
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

    @staticmethod
    def update_weight_collected(collector_id, weight):
        """Adds the weight of a completed transaction to the collector's total."""
        sql = "UPDATE collectors SET total_weight_collected = total_weight_collected + %s WHERE collector_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (weight, collector_id))
                db.commit()

    @staticmethod
    def update_profile(collector_id, **kwargs):
        """Updates collector profile information."""
        allowed_fields = ['name', 'phone', 'vehicle_number', 'waste_types_collected', 'bio', 'profile_image',
                         'latitude', 'longitude', 'address', 'city', 'state', 'pincode', 'service_radius_km']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if field == 'waste_types_collected' and isinstance(value, list):
                    updates.append(f"{field} = %s")
                    params.append(value)
                else:
                    updates.append(f"{field} = %s")
                    params.append(value)
        
        if not updates:
            return
            
        params.append(collector_id)
        sql = f"UPDATE collectors SET {', '.join(updates)} WHERE collector_id = %s"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, params)
                db.commit()

    @staticmethod
    def update_location(collector_id, latitude, longitude, address=None, city=None, state=None, pincode=None, service_radius_km=50.0):
        """Updates collector location information."""
        sql = """
            UPDATE collectors 
            SET latitude = %s, longitude = %s, address = %s, city = %s, state = %s, pincode = %s, service_radius_km = %s
            WHERE collector_id = %s
        """
        params = (latitude, longitude, address, city, state, pincode, service_radius_km, collector_id)
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, params)
                db.commit()

    @staticmethod
    def get_location(collector_id):
        """Gets collector location information."""
        sql = """
            SELECT latitude, longitude, address, city, state, pincode, service_radius_km
            FROM collectors 
            WHERE collector_id = %s
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (collector_id,))
                return cursor.fetchone()

    @staticmethod
    def update_password(collector_id, new_password):
        """Updates collector password."""
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = "UPDATE collectors SET password_hash = %s WHERE collector_id = %s"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (password_hash, collector_id))
                db.commit()

    @staticmethod
    def get_leaderboard(limit=100):
        """Gets the national collector leaderboard, ranked by weight collected."""
        sql = """
            SELECT collector_id, name, total_weight_collected
            FROM collectors
            WHERE is_active = TRUE
            ORDER BY total_weight_collected DESC
            LIMIT %s
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (limit,))
                return cursor.fetchall()