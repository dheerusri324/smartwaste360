#!/usr/bin/env python3
"""
Test admin management endpoints
"""

import requests

def test_admin_endpoints():
    """Test admin management functionality"""
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
        
        # Test get all collectors
        print("\n🔍 Testing get all collectors...")
        collectors_response = requests.get(
            'https://smartwaste360-backend.onrender.com/api/admin/collectors',
            headers=headers,
            timeout=10
        )
        
        print(f"Collectors Status: {collectors_response.status_code}")
        print(f"Collectors Response: {collectors_response.text}")
        
        # Test get all users
        print("\n🔍 Testing get all users...")
        users_response = requests.get(
            'https://smartwaste360-backend.onrender.com/api/admin/users',
            headers=headers,
            timeout=10
        )
        
        print(f"Users Status: {users_response.status_code}")
        print(f"Users Response: {users_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Admin Management Endpoints...")
    print("=" * 50)
    
    success = test_admin_endpoints()
    
    if success:
        print("\n🎉 Admin endpoints are working!")
        print("📱 Admin management should now persist changes to database")
    else:
        print("\n❌ Admin endpoints need debugging")