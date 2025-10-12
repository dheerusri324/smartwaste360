#!/usr/bin/env python3
"""
Create admin with exact credentials mentioned
"""

import requests

def create_exact_admin():
    """Create admin with exact credentials"""
    try:
        # Register admin with exact credentials
        register_data = {
            "role": "admin",
            "username": "admin",
            "email": "admin@gmail.com",
            "password": "admin",
            "full_name": "Admin User"
        }
        
        print("🔧 Creating admin with exact credentials...")
        register_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/auth/register',
            json=register_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Register Status: {register_response.status_code}")
        if register_response.status_code == 409:
            print("ℹ️ Admin already exists, testing login...")
        elif register_response.status_code == 201:
            print("✅ Admin created successfully!")
        else:
            print(f"❌ Registration failed: {register_response.text}")
            return False
        
        # Test login
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
        if login_response.status_code == 200:
            print("✅ Admin login working!")
            return True
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Admin with Exact Credentials...")
    print("=" * 50)
    
    success = create_exact_admin()
    
    if success:
        print("\n🎉 Admin ready!")
        print("📱 Mobile admin login:")
        print("   URL: https://smartwaste360-frontend.vercel.app/admin/login")
        print("   Email: admin@gmail.com")
        print("   Password: admin")
        print("\n💡 Important: Use the ADMIN login page, not user login!")
    else:
        print("\n❌ Admin setup failed")