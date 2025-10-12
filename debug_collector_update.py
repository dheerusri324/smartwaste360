#!/usr/bin/env python3
"""
Debug script to test collector status update with detailed error logging
"""

import requests
import json

# Configuration
BASE_URL = "https://smartwaste360-backend.onrender.com/api"
ADMIN_EMAIL = "admin@smartwaste360.com"
ADMIN_PASSWORD = "admin123"

def debug_collector_update():
    print("🔍 Debugging Collector Status Update...")
    print("=" * 60)
    
    # Step 1: Login as admin
    print("🔐 Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful!")
    
    # Step 2: Get collectors
    print("\n📋 Getting current collectors...")
    collectors_response = requests.get(f"{BASE_URL}/admin/collectors", headers=headers)
    
    if collectors_response.status_code != 200:
        print(f"❌ Failed to get collectors: {collectors_response.status_code}")
        print(f"Response: {collectors_response.text}")
        return
    
    collectors = collectors_response.json()
    print(f"✅ Found {len(collectors)} collectors")
    
    if not collectors:
        print("❌ No collectors found to test")
        return
    
    # Step 3: Test status update with detailed debugging
    collector = collectors[0]
    collector_id = collector['id']
    current_status = collector['is_active']
    new_status = not current_status
    
    print(f"\n🔄 Testing status update for collector ID: {collector_id}")
    print(f"Current status: {current_status}")
    print(f"New status: {new_status}")
    
    # Test the update
    update_data = {"is_active": new_status}
    print(f"Sending PUT request to: {BASE_URL}/admin/collectors/{collector_id}/status")
    print(f"Data: {json.dumps(update_data)}")
    print(f"Headers: Authorization: Bearer {token[:20]}...")
    
    update_response = requests.put(
        f"{BASE_URL}/admin/collectors/{collector_id}/status",
        json=update_data,
        headers=headers
    )
    
    print(f"\nResponse Status: {update_response.status_code}")
    print(f"Response Headers: {dict(update_response.headers)}")
    print(f"Response Body: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✅ Status update successful!")
        
        # Verify the change
        print("\n🔍 Verifying the change...")
        verify_response = requests.get(f"{BASE_URL}/admin/collectors", headers=headers)
        if verify_response.status_code == 200:
            updated_collectors = verify_response.json()
            updated_collector = next((c for c in updated_collectors if c['id'] == collector_id), None)
            if updated_collector:
                print(f"Updated status: {updated_collector['is_active']}")
                if updated_collector['is_active'] == new_status:
                    print("✅ Status change verified!")
                else:
                    print("❌ Status change not reflected in database")
            else:
                print("❌ Collector not found in updated list")
        else:
            print(f"❌ Failed to verify change: {verify_response.status_code}")
    else:
        print("❌ Status update failed")
        
        # Try to parse error details
        try:
            error_data = update_response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")

if __name__ == "__main__":
    debug_collector_update()