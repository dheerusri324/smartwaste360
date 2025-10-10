# backend/models/transaction.py

from config.database import get_db
import json
from psycopg2.extras import RealDictCursor

class Transaction:
    @staticmethod
    def create_transaction(user_id, booking_id, collector_id, weight_deposited,
                           points_earned, materials, verification_code):
        """Creates a new transaction in the user_transactions table."""
        sql = """
            INSERT INTO user_transactions 
            (user_id, booking_id, collector_id, weight_deposited, 
             points_earned, materials, verification_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """
        materials_json = json.dumps(materials)
        params = (user_id, booking_id, collector_id, weight_deposited,
                  points_earned, materials_json, verification_code)
        
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                transaction_id = cursor.fetchone()['transaction_id']
                db.commit()
                return transaction_id

    @staticmethod
    def get_user_transactions(user_id, page=1, limit=10):
        """Gets a paginated list of transactions for a specific user."""
        offset = (page - 1) * limit
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM user_transactions WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                total = result['total'] if result else 0
                
                sql = "SELECT * FROM user_transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
                cursor.execute(sql, (user_id, limit, offset))
                transactions = cursor.fetchall()
                
                return { "transactions": transactions, "total": total, "page": page, "total_pages": (total + limit - 1) // limit }

    # --- NEW METHOD FOR COLLECTORS ---
    @staticmethod
    def get_transactions_by_collector(collector_id, page=1, limit=10):
        """Gets a paginated list of transactions handled by a specific collector."""
        offset = (page - 1) * limit
        with get_db() as db:
            if not db: raise ConnectionError("Database connection not available.")
            with db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM user_transactions WHERE collector_id = %s", (collector_id,))
                result = cursor.fetchone()
                total = result['total'] if result else 0

                # Join with the users table to get the user's name for each transaction
                sql = """
                    SELECT t.*, u.full_name as user_full_name
                    FROM user_transactions t
                    JOIN users u ON t.user_id = u.user_id
                    WHERE t.collector_id = %s
                    ORDER BY t.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (collector_id, limit, offset))
                transactions = cursor.fetchall()

                return { "transactions": transactions, "total": total, "page": page, "total_pages": (total + limit - 1) // limit }