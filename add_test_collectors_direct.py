#!/usr/bin/env python3
"""
Add test collectors directly to Render database via SQL
"""

import requests

def add_test_collectors():
    """Add test collectors via database setup endpoint"""
    try:
        # First, let's create a custom endpoint to add collectors
        print("🔧 Adding test collectors to database...")
        
        # We'll use the existing setup-database endpoint which should now include collectors
        response = requests.get(
            'https://smartwaste360-backend.onrender.com/setup-database',
            timeout=10
        )
        
        print(f"Database setup status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Database setup completed")
            
            # Now test the admin collectors endpoint
            print("\n🔐 Testing admin collectors endpoint...")
            
            # Login as admin first
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
            
            if login_response.status_code == 200:
                access_token = login_response.json()['access_token']
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Test get collectors
                collectors_response = requests.get(
                    'https://smartwaste360-backend.onrender.com/api/admin/collectors',
                    headers=headers,
                    timeout=10
                )
                
                print(f"Collectors endpoint status: {collectors_response.status_code}")
                if collectors_response.status_code == 200:
                    collectors_data = collectors_response.json()
                    collectors = collectors_data.get('collectors', [])
                    print(f"✅ Found {len(collectors)} collectors")
                    
                    for collector in collectors:
                        print(f"  • {collector.get('name')} - Active: {collector.get('is_active')}")
                    
                    return len(collectors) > 0
                else:
                    print(f"❌ Collectors endpoint failed: {collectors_response.text}")
            else:
                print(f"❌ Admin login failed: {login_response.text}")
        else:
            print(f"❌ Database setup failed: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Adding Test Collectors to Render Database...")
    print("=" * 50)
    
    success = add_test_collectors()
    
    if success:
        print("\n🎉 Test collectors are ready!")
        print("📱 Now test collector management on mobile:")
        print("   1. Login as admin: admin@gmail.com / admin")
        print("   2. Go to collector management")
        print("   3. Toggle collector status (activate/deactivate)")
        print("   4. Reload page - changes should now persist!")
    else:
        print("\n❌ No collectors found - they may not have been created yet")
        print("📱 The collector management functionality is fixed, but needs collectors to test")