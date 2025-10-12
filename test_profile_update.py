#!/usr/bin/env python3
"""
Test profile update functionality
"""

import requests
import json

def test_profile_update():
    """Test profile update for lol user"""
    try:
        # First, login to get the access token
        print("🔐 Logging in as 'lol' user...")
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
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
        login_data = login_response.json()
        access_token = login_data['access_token']
        print("✅ Login successful!")
        
        # Now try to update the profile
        print("\n📝 Updating profile (full_name: 'LOL User' -> 'lol')...")
        
        update_data = {
            "full_name": "lol"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        update_response = requests.put(
            'https://smartwaste360-backend.onrender.com/api/auth/profile',
            json=update_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Update Status: {update_response.status_code}")
        print(f"Update Response: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ Profile update successful!")
            
            # Verify the update by getting profile
            print("\n🔍 Verifying profile update...")
            profile_response = requests.get(
                'https://smartwaste360-backend.onrender.com/api/auth/profile',
                headers=headers,
                timeout=10
            )
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"✅ Current full_name: {profile_data.get('user', {}).get('full_name', 'Not found')}")
                return True
            else:
                print(f"❌ Profile verification failed: {profile_response.text}")
                return False
        else:
            print(f"❌ Profile update failed: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Profile Update for 'lol' user...")
    print("=" * 50)
    
    success = test_profile_update()
    
    if success:
        print("\n🎉 Profile update is working!")
        print("📱 The mobile app should now work for profile updates")
    else:
        print("\n❌ Profile update failed - needs debugging")
        print("📱 Try refreshing the mobile app and try again")