#!/usr/bin/env python3
"""
Simple test to create one collector step by step
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_simple_collector():
    print("🧪 Testing Simple Collector Creation...")
    print("=" * 60)
    
    # Test with minimal data first
    collector_data = {
        "role": "collector",
        "full_name": "Simple Test",
        "phone": "1234567890", 
        "email": "simple@test.com",
        "password": "test123"
    }
    
    print("📝 Sending registration request...")
    print(f"Data: {json.dumps(collector_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=collector_data, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Collector created successfully!")
            
            # Test login
            print("\n🔐 Testing login...")
            login_data = {
                "email": collector_data["email"],
                "password": collector_data["password"]
            }
            
            login_response = requests.post(f"{BASE_URL}/collector/login", json=login_data)
            print(f"Login Status: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_simple_collector()