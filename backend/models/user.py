# backend/models/user.py

from config.database import get_db # <-- CORRECTED IMPORT
import bcrypt
from psycopg2.extras import RealDictCursor

class User:
    @staticmethod
    def create_user(username, email, password, full_name, colony_id, phone=None):
        """Create a new user in the database"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = """
            INSERT INTO users (username, email, password_hash, full_name, colony_id, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (username, email, password_hash, full_name, colony_id, phone))
                user_id = cursor.fetchone()['user_id']
                db.commit()
                return user_id

    @staticmethod
    def get_user_by_id(user_id):
        """Get a single user by their ID."""
        sql = "SELECT * FROM users WHERE user_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()

    @staticmethod
    def get_user_by_username_or_email(identifier):
        """Get a single user by their username or email."""
        sql = "SELECT * FROM users WHERE username = %s OR email = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (identifier, identifier))
                return cursor.fetchone()

    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify a provided password against a stored hash."""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

    @staticmethod
    def update_last_login(user_id):
        """Update the last_login timestamp for a user."""
        sql = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                db.commit()

    @staticmethod
    def update_user_points(user_id, points, weight):
        """Update a user's points and total recycled weight."""
        sql = """
            UPDATE users 
            SET total_points = total_points + %s,
                total_weight_recycled = total_weight_recycled + %s
            WHERE user_id = %s
        """
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (points, weight, user_id))
                db.commit()

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user profile information."""
        allowed_fields = ['full_name', 'phone']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return
            
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, params)
                db.commit()

    @staticmethod
    def update_password(user_id, new_password):
        """Update user password."""
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor() as cursor:
                cursor.execute(sql, (password_hash, user_id))
                db.commit()