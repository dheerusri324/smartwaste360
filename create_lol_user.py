#!/usr/bin/env python3
"""
Create the 'lol' user for mobile testing
"""

import requests
import json

def create_lol_user():
    """Create the lol user via API"""
    try:
        # Register the lol user
        register_data = {
            "username": "lol",
            "email": "lol@smartwaste360.com", 
            "password": "lol123",  # Simple password for testing
            "full_name": "LOL User",
            "latitude": 17.385044,  # Hyderabad coordinates
            "longitude": 78.486671,
            "role": "user"
        }
        
        print("🔧 Creating 'lol' user...")
        register_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/auth/register',
            json=register_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Register Status: {register_response.status_code}")
        print(f"Register Response: {register_response.text}")
        
        if register_response.status_code == 201:
            print("✅ User 'lol' created successfully!")
            
            # Test login
            print("\n🔐 Testing login for 'lol' user...")
            login_data = {
                "identifier": "lol@smartwaste360.com",
                "password": "lol123"
            }
            
            login_response = requests.post(
                'https://smartwaste360-backend.onrender.com/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Login Status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("✅ Login test successful!")
                return True
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
                
        elif register_response.status_code == 409:
            print("ℹ️ User 'lol' already exists, testing login...")
            
            # Test login with existing user
            login_data = {
                "identifier": "lol@smartwaste360.com",
                "password": "lol123"
            }
            
            login_response = requests.post(
                'https://smartwaste360-backend.onrender.com/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code == 200:
                print("✅ Existing user login successful!")
                return True
            else:
                print("❌ Existing user login failed - password might be different")
                print("Try these credentials on mobile:")
                print("   Email: lol@smartwaste360.com")
                print("   Password: lol123")
                return False
        else:
            print(f"❌ Registration failed: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Creating 'lol' user for SmartWaste360...")
    print("=" * 50)
    
    success = create_lol_user()
    
    if success:
        print("\n🎉 'lol' user is ready!")
        print("📱 Mobile login credentials:")
        print("   Email: lol@smartwaste360.com")
        print("   Password: lol123")
        print("\n💡 Note: Use EMAIL for login, not username!")
    else:
        print("\n❌ Failed to create/verify 'lol' user")
        print("📱 Try the test user instead:")
        print("   Email: test@smartwaste360.com")
        print("   Password: test123")