#!/usr/bin/env python3
"""
Create test collectors for admin management testing
"""

import requests

def create_test_collectors():
    """Create test collectors"""
    try:
        collectors = [
            {
                "role": "collector",
                "full_name": "John Collector",
                "phone": "9876543210",
                "email": "john@collector.com",
                "password": "collector123",
                "vehicle_number": "AP01AB1234"
            },
            {
                "role": "collector", 
                "full_name": "Jane Collector",
                "phone": "9876543211",
                "email": "jane@collector.com", 
                "password": "collector123",
                "vehicle_number": "AP01AB5678"
            }
        ]
        
        for collector in collectors:
            print(f"🔧 Creating collector: {collector['full_name']}")
            response = requests.post(
                'https://smartwaste360-backend.onrender.com/api/auth/register',
                json=collector,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code in [201, 409]:  # Created or already exists
                print(f"✅ {collector['full_name']} ready")
            else:
                print(f"❌ Failed: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Test Collectors...")
    print("=" * 50)
    create_test_collectors()
    print("\n🎉 Test collectors created!")
    print("📱 Now test admin collector management on mobile")