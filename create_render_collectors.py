#!/usr/bin/env python3
"""
Create test collectors directly in Render database
"""

import requests

def create_test_collectors():
    """Create test collectors via Render API"""
    try:
        # Login as admin first
        print("🔐 Logging in as admin...")
        login_data = {
            "email": "admin@gmail.com",
            "password": "admin"
        }
        
        login_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/admin/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.text}")
            return False
            
        access_token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Admin login successful!")
        
        # Create test collectors via auth/register
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
        
        # Now test getting collectors
        print("\n🔍 Testing get all collectors...")
        collectors_response = requests.get(
            'https://smartwaste360-backend.onrender.com/api/admin/collectors',
            headers=headers,
            timeout=10
        )
        
        print(f"Collectors Status: {collectors_response.status_code}")
        if collectors_response.status_code == 200:
            collectors_data = collectors_response.json()
            print(f"Found {len(collectors_data.get('collectors', []))} collectors")
            for collector in collectors_data.get('collectors', []):
                print(f"  • {collector.get('name')} - Active: {collector.get('is_active')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Test Collectors for Render...")
    print("=" * 50)
    
    success = create_test_collectors()
    
    if success:
        print("\n🎉 Test collectors created!")
        print("📱 Now test admin collector management on mobile:")
        print("   1. Login as admin: admin@gmail.com / admin")
        print("   2. Go to collector management")
        print("   3. Toggle collector status (activate/deactivate)")
        print("   4. Reload page - changes should persist!")
    else:
        print("\n❌ Failed to create test collectors")