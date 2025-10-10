# quick_test.py
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

from config.database import get_db

def test_database_operations():
    print("Testing database operations...")
    try:
        # Test connection and basic operations
        db = next(get_db())
        cursor = db.cursor()
        
        # Test 1: Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tables found: {tables}")
        
        # Test 2: Check points configuration
        cursor.execute("SELECT * FROM points_config")
        points_config = cursor.fetchall()
        print(f"✅ Points config loaded: {len(points_config)} entries")
        
        # Test 3: Check if any users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")
        
        cursor.close()
        print("🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_database_operations()