#!/usr/bin/env python3
"""
Simple test for collection completion with minimal data
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_simple_collection():
    print("🧪 Testing Simple Collection Completion...")
    print("=" * 60)
    
    # Login as collector
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
    
    # Test with minimal data
    collection_data = {
        "colony_id": 1,
        "total_weight": 10.0,
        "waste_types": {
            "plastic": 5.0
        }
    }
    
    print(f"Testing with data: {json.dumps(collection_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/collector/complete-collection",
        json=collection_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Collection completion working!")
    else:
        print("❌ Collection completion failed")
        
        # Try to get more details
        if response.status_code == 404:
            print("Endpoint not found - deployment might not be complete")
        elif response.status_code == 500:
            print("Internal server error - check backend logs")

if __name__ == "__main__":
    test_simple_collection()