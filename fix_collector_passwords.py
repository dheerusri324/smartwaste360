#!/usr/bin/env python3
"""
Fix collector passwords by creating new collectors with proper password hashes
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def fix_collector_passwords():
    print("🔧 Fixing Collector Passwords...")
    print("=" * 60)
    
    # Create new collectors with known passwords using the auth/register endpoint
    collectors_to_create = [
        {
            "role": "collector",
            "full_name": "John Test Collector",
            "phone": "9876543210",
            "email": "john.test@collector.com",
            "password": "collector123",
            "vehicle_number": "AP01AB1234"
        },
        {
            "role": "collector", 
            "full_name": "Jane Test Collector",
            "phone": "9876543211",
            "email": "jane.test@collector.com",
            "password": "collector123",
            "vehicle_number": "AP01AB5678"
        }
    ]
    
    for collector_data in collectors_to_create:
        print(f"\n👤 Creating collector: {collector_data['full_name']}")
        
        # Register the collector
        register_response = requests.post(f"{BASE_URL}/auth/register", json=collector_data)
        print(f"Register Status: {register_response.status_code}")
        
        if register_response.status_code == 201:
            print(f"✅ Collector created successfully")
            
            # Test login immediately
            login_data = {
                "email": collector_data["email"],
                "password": collector_data["password"]
            }
            
            login_response = requests.post(f"{BASE_URL}/collector/login", json=login_data)
            print(f"Login Test Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print(f"✅ Login test successful!")
            else:
                print(f"❌ Login test failed: {login_response.text}")
                
        elif register_response.status_code == 409:
            print(f"⚠️ Collector already exists, testing login...")
            
            # Test login with existing collector
            login_data = {
                "email": collector_data["email"],
                "password": collector_data["password"]
            }
            
            login_response = requests.post(f"{BASE_URL}/collector/login", json=login_data)
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print(f"✅ Login successful!")
            else:
                print(f"❌ Login failed: {login_response.text}")
        else:
            print(f"❌ Registration failed: {register_response.text}")

if __name__ == "__main__":
    fix_collector_passwords()