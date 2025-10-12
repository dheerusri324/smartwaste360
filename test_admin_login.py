#!/usr/bin/env python3
"""
Test admin login functionality and create admin if needed
"""

import requests
import json

def test_admin_functionality():
    """Test admin registration and login"""
    try:
        # First, try to register the admin
        print("🔧 Attempting to register admin...")
        register_data = {
            "role": "admin",
            "username": "admin",
            "email": "admin@gmail.com",
            "password": "admin",
            "full_name": "System Administrator"
        }
        
        register_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/auth/register',
            json=register_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Register Status: {register_response.status_code}")
        print(f"Register Response: {register_response.text}")
        
        # Now try to login with admin credentials
        print("\n🔐 Attempting admin login...")
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
        
        print(f"Login Status: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        if login_response.status_code == 200:
            print("✅ Admin login successful!")
            
            # Test admin profile access
            login_data = login_response.json()
            access_token = login_data['access_token']
            
            print("\n🔍 Testing admin profile access...")
            profile_response = requests.get(
                'https://smartwaste360-backend.onrender.com/api/admin/profile',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            print(f"Profile Status: {profile_response.status_code}")
            print(f"Profile Response: {profile_response.text}")
            
            if profile_response.status_code == 200:
                print("✅ Admin profile access successful!")
                return True
            else:
                print("❌ Admin profile access failed")
                return False
        else:
            print(f"❌ Admin login failed with status {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Admin Login for SmartWaste360...")
    print("=" * 50)
    
    success = test_admin_functionality()
    
    if success:
        print("\n🎉 Admin authentication is working!")
        print("📱 Try these admin credentials on mobile:")
        print("   Email: admin@gmail.com")
        print("   Password: admin")
        print("\n💡 Make sure to use the ADMIN login form, not user login!")
    else:
        print("\n❌ Admin authentication needs debugging")
        print("📱 Check the mobile console for more details")