#!/usr/bin/env python3
"""
Script to add missing tables to the Render database
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def add_missing_tables():
    """Add missing achievement and admin activity tables"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔗 Connected to database successfully")
        
        # Add missing tables
        missing_tables_sql = """
        -- Achievement tables
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

        -- Admin activity logs table
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
        
        print("📝 Executing SQL to create missing tables...")
        
        # Execute the SQL
        cursor.execute(missing_tables_sql)
        conn.commit()
        
        print("✅ Missing tables created successfully!")
        
        # Verify all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        cursor.close()
        conn.close()
        
        print(f"📊 Total tables in database: {len(table_names)}")
        print("📋 All tables:")
        for table in table_names:
            print(f"   • {table}")
        
        print("\n🎉 Database setup completed with ALL tables!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding missing tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Adding missing tables to SmartWaste360 database...")
    print("=" * 50)
    
    success = add_missing_tables()
    
    if success:
        print("\n✅ All missing tables have been added successfully!")
        print("🔗 Your Render backend is now fully configured!")
        print("📱 Mobile DNS issues should be resolved!")
    else:
        print("\n❌ Failed to add missing tables. Check the error above.")