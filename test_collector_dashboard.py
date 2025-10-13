#!/usr/bin/env python3
"""
Test collector dashboard endpoints
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_collector_dashboard():
    print("🚛 Testing Collector Dashboard...")
    print("=" * 60)
    
    # Step 1: Login as collector
    print("🔐 Logging in as collector...")
    login_response = requests.post(f"{BASE_URL}/collector/login", json={
        "email": "newtest@collector.com",
        "password": "test123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Collector login successful!")
    
    # Step 2: Test ready-colonies endpoint
    print("\n📍 Testing ready-colonies endpoint...")
    colonies_response = requests.get(f"{BASE_URL}/collector/ready-colonies", headers=headers)
    
    print(f"Status: {colonies_response.status_code}")
    print(f"Response: {colonies_response.text}")
    
    if colonies_response.status_code == 200:
        print("✅ Ready colonies endpoint working!")
        colonies_data = colonies_response.json()
        colonies = colonies_data.get('colonies', [])
        print(f"Found {len(colonies)} ready colonies")
    else:
        print("❌ Ready colonies endpoint failed")
        
    # Step 3: Test other collector endpoints
    print("\n📊 Testing collector profile...")
    profile_response = requests.get(f"{BASE_URL}/collector/profile", headers=headers)
    print(f"Profile Status: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        print("✅ Profile endpoint working!")
    else:
        print(f"❌ Profile endpoint failed: {profile_response.text}")

if __name__ == "__main__":
    test_collector_dashboard()