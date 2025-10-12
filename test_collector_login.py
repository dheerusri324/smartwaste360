#!/usr/bin/env python3
"""
Test collector login and registration
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_collector_operations():
    print("🚛 Testing Collector Operations...")
    print("=" * 60)
    
    # Test 1: Try to register a new collector
    print("👤 Testing collector registration...")
    register_data = {
        "role": "collector",
        "full_name": "Test Collector",
        "phone": "9999999999",
        "email": "testcollector@example.com",
        "password": "testpass123",
        "vehicle_number": "AP01TEST123"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register Status: {register_response.status_code}")
    print(f"Register Response: {register_response.text}")
    
    # Test 2: Try to login with existing collector
    print("\n🔐 Testing collector login...")
    login_data = {
        "email": "john@collector.com",
        "password": "collector123"
    }
    
    login_response = requests.post(f"{BASE_URL}/collector/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    # Test 3: Try different collector credentials
    print("\n🔐 Testing with different collector...")
    login_data2 = {
        "email": "jane@collector.com", 
        "password": "collector123"
    }
    
    login_response2 = requests.post(f"{BASE_URL}/collector/login", json=login_data2)
    print(f"Login Status 2: {login_response2.status_code}")
    print(f"Login Response 2: {login_response2.text}")

if __name__ == "__main__":
    test_collector_operations()