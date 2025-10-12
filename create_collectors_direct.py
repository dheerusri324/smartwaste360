#!/usr/bin/env python3
"""
Create collectors directly in database
"""

import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def create_collectors_direct():
    """Create collectors directly in database"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        collectors = [
            {
                'collector_id': 'COL001',
                'name': 'John Collector',
                'phone': '9876543210',
                'email': 'john@collector.com',
                'password': 'collector123',
                'vehicle_number': 'AP01AB1234'
            },
            {
                'collector_id': 'COL002', 
                'name': 'Jane Collector',
                'phone': '9876543211',
                'email': 'jane@collector.com',
                'password': 'collector123',
                'vehicle_number': 'AP01AB5678'
            }
        ]
        
        for collector in collectors:
            # Hash password
            password_hash = bcrypt.hashpw(collector['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert collector
            cursor.execute("""
                INSERT INTO collectors (collector_id, name, phone, email, password_hash, vehicle_number, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (collector_id) DO NOTHING
            """, (
                collector['collector_id'],
                collector['name'],
                collector['phone'], 
                collector['email'],
                password_hash,
                collector['vehicle_number'],
                True
            ))
            
            print(f"✅ Created collector: {collector['name']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Test collectors created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Test Collectors Directly...")
    print("=" * 50)
    
    success = create_collectors_direct()
    
    if success:
        print("📱 Now test admin collector management on mobile!")
    else:
        print("❌ Failed to create collectors")