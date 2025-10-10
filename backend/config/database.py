# backend/config/database.py

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from pathlib import Path
from contextlib import contextmanager

# Load environment variables from the project root .env file
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'dheerusri'),
    'database': os.getenv('DB_NAME', 'smartwaste360'),
    'port': os.getenv('DB_PORT', '5432')
}

def create_connection_pool():
    """Initializes the connection pool."""
    try:
        connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, connection_string)
        
        # Test the connection
        conn = connection_pool.getconn()
        # Replaced emoji with simple text for Windows compatibility
        print(f"[OK] Database connection pool created successfully for '{conn.get_dsn_parameters()['dbname']}'.")
        connection_pool.putconn(conn)
        
        return connection_pool
    except Exception as e:
        # Replaced emoji with simple text
        print(f"[ERROR] Error creating connection pool: {e}")
        return None

# Initialize the pool when the application starts
connection_pool = create_connection_pool()

@contextmanager
def get_db():
    """
    Provides a database connection from the pool using a context manager.
    """
    if not connection_pool:
        raise Exception("Database connection pool is not available.")

    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    finally:
        if connection:
            connection_pool.putconn(connection)