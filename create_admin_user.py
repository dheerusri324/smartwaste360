#!/usr/bin/env python3
"""
Script to create admin user and test collector status update
"""

import requests
import json

# Configuration
BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def create_admin_and_test():
    print("🔧 Creating Admin User and Testing Collector Update...")
    print("=" * 60)
    
    # Step 1: Create admin user
    print("👤 Creating admin user...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "admin",
        "email": "admin@smartwaste360.com",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "admin"
    })
    
    print(f"Register Status: {register_response.status_code}")
    print(f"Register Response: {register_response.text}")
    
    # Step 2: Login as admin
    print("\n🔐 Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": "admin@smartwaste360.com",
        "password": "admin123"
    })
    
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code != 200:
        print("❌ Login failed, cannot proceed with testing")
        return
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful!")
    
    # Step 3: Get collectors
    print("\n📋 Getting current collectors...")
    collectors_response = requests.get(f"{BASE_URL}/admin/collectors", headers=headers)
    
    print(f"Collectors Status: {collectors_response.status_code}")
    print(f"Collectors Response: {collectors_response.text}")
    
    if collectors_response.status_code != 200:
        print("❌ Failed to get collectors")
        return
    
    collectors = collectors_response.json()
    print(f"✅ Found {len(collectors)} collectors")
    
    if not collectors:
        print("❌ No collectors found to test")
        return
    
    # Step 4: Test status update
    collector = collectors[0]
    collector_id = collector['id']
    current_status = collector['is_active']
    new_status = not current_status
    
    print(f"\n🔄 Testing status update for collector ID: {collector_id}")
    print(f"Current status: {current_status}")
    print(f"New status: {new_status}")
    
    update_data = {"is_active": new_status}
    update_response = requests.put(
        f"{BASE_URL}/admin/collectors/{collector_id}/status",
        json=update_data,
        headers=headers
    )
    
    print(f"\nUpdate Status: {update_response.status_code}")
    print(f"Update Response: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✅ Collector status update successful!")
    else:
        print("❌ Collector status update failed")

if __name__ == "__main__":
    create_admin_and_test()