#!/usr/bin/env python3
"""
Simple test to check admin login only
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_admin_login():
    print("🔐 Testing admin login...")
    
    # Check API version first
    try:
        version_response = requests.get("https://smartwaste360-backend.onrender.com/")
        version_data = version_response.json()
        print(f"API Version: {version_data.get('version', 'unknown')}")
        print(f"Deployment: {version_data.get('deployment', 'unknown')}")
    except:
        print("Could not get version info")
    
    # Test admin login
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": "admin@gmail.com",
        "password": "admin"
    })
    
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code == 200:
        print("✅ Admin login successful!")
        token = login_response.json().get('access_token')
        print(f"Token received: {token[:50]}..." if token else "No token received")
        return token
    else:
        print("❌ Admin login failed")
        return None

if __name__ == "__main__":
    test_admin_login()