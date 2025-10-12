#!/usr/bin/env python3
"""
Test database connection and collector data directly
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_database():
    print("🔍 Testing Database and Collector Data...")
    print("=" * 60)
    
    # First login as admin to get collectors list
    print("🔐 Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": "admin@gmail.com",
        "password": "admin"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.text}")
        return
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful!")
    
    # Get collectors from admin endpoint
    print("\n📋 Getting collectors from admin endpoint...")
    collectors_response = requests.get(f"{BASE_URL}/admin/collectors", headers=headers)
    print(f"Admin collectors status: {collectors_response.status_code}")
    
    if collectors_response.status_code == 200:
        collectors_data = collectors_response.json()
        collectors = collectors_data.get('collectors', [])
        print(f"Found {len(collectors)} collectors:")
        for collector in collectors:
            print(f"  - {collector.get('name')} ({collector.get('email')}) - Active: {collector.get('is_active')}")
            
        # Try to login with the first collector
        if collectors:
            first_collector = collectors[0]
            print(f"\n🔐 Testing login with collector: {first_collector.get('email')}")
            
            # Try common passwords
            test_passwords = ["collector123", "password", "123456", "collector", "test123"]
            
            for password in test_passwords:
                login_data = {
                    "email": first_collector.get('email'),
                    "password": password
                }
                
                login_response = requests.post(f"{BASE_URL}/collector/login", json=login_data)
                print(f"  Password '{password}': {login_response.status_code}")
                
                if login_response.status_code == 200:
                    print(f"  ✅ Login successful with password: {password}")
                    break
                elif login_response.status_code == 401:
                    print(f"  ❌ Invalid credentials")
                else:
                    print(f"  ❌ Error: {login_response.text}")
    else:
        print(f"❌ Failed to get collectors: {collectors_response.text}")

if __name__ == "__main__":
    test_database()