#!/usr/bin/env python3
"""
Check if there are any users in the database
"""

import requests
import json

def check_users():
    """Check users via API"""
    try:
        # Test if we can reach the backend
        response = requests.get('https://smartwaste360-backend.onrender.com/', timeout=10)
        print("✅ Backend reachable:", response.status_code)
        
        # Try to register a test user
        register_data = {
            "username": "testuser",
            "email": "test@smartwaste360.com", 
            "password": "test123",
            "full_name": "Test User",
            "latitude": 17.385044,
            "longitude": 78.486671,
            "role": "user"
        }
        
        print("\n🔧 Attempting to register test user...")
        register_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/auth/register',
            json=register_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Register Status: {register_response.status_code}")
        print(f"Register Response: {register_response.text}")
        
        # Try to login with test user
        print("\n🔐 Attempting to login with test user...")
        login_data = {
            "identifier": "test@smartwaste360.com",
            "password": "test123"
        }
        
        login_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Login Status: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        if login_response.status_code == 200:
            print("\n✅ SUCCESS! Test user login works!")
            return True
        else:
            print(f"\n❌ Login failed with status {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Checking SmartWaste360 User Authentication...")
    print("=" * 50)
    
    success = check_users()
    
    if success:
        print("\n🎉 Authentication is working!")
        print("📱 Try these credentials on mobile:")
        print("   Email: test@smartwaste360.com")
        print("   Password: test123")
    else:
        print("\n❌ Authentication needs debugging")