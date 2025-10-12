#!/usr/bin/env python3
"""
Database table creation script for Railway PostgreSQL
Run this to create all required tables
"""

import os
import psycopg2
from pathlib import Path

def create_tables():
    """Create all database tables using the migration SQL"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Read the SQL migration file
        sql_file = Path(__file__).parent / 'database' / 'migrations' / '001_initial_schema.sql'
        print(f"📖 Reading SQL file: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL
        print("🚀 Creating database tables...")
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Created tables: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_tables()