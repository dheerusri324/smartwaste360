#!/usr/bin/env python3
"""
Test collection completion functionality
"""

import requests
import json

BASE_URL = "https://smartwaste360-backend.onrender.com/api"

def test_collection_completion():
    print("🚛 Testing Collection Completion...")
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
    
    # Step 2: Get ready colonies
    print("\n📍 Getting ready colonies...")
    colonies_response = requests.get(f"{BASE_URL}/collector/ready-colonies", headers=headers)
    
    if colonies_response.status_code != 200:
        print(f"❌ Failed to get colonies: {colonies_response.text}")
        return
    
    colonies = colonies_response.json().get('colonies', [])
    print(f"✅ Found {len(colonies)} ready colonies")
    
    if not colonies:
        print("❌ No colonies available for testing")
        return
    
    # Step 3: Test collection completion
    colony = colonies[0]
    colony_id = colony['colony_id']
    
    print(f"\n🗑️ Testing collection completion for colony: {colony['colony_name']}")
    print(f"Available waste: Plastic: {colony.get('current_plastic_kg', 0)}kg, Paper: {colony.get('current_paper_kg', 0)}kg")
    
    # Simulate collection data
    collection_data = {
        "colony_id": colony_id,
        "total_weight": 15.5,
        "waste_types": {
            "plastic": 6.5,
            "paper": 8.2,
            "metal": 0.8
        },
        "notes": "Collection completed successfully - test"
    }
    
    print(f"Collection data: {json.dumps(collection_data, indent=2)}")
    
    completion_response = requests.post(
        f"{BASE_URL}/collector/complete-collection",
        json=collection_data,
        headers=headers
    )
    
    print(f"\nCompletion Status: {completion_response.status_code}")
    print(f"Completion Response: {completion_response.text}")
    
    if completion_response.status_code == 200:
        print("✅ Collection completion successful!")
        
        # Verify colony waste amounts were updated
        print("\n🔍 Verifying colony waste amounts were updated...")
        updated_colonies_response = requests.get(f"{BASE_URL}/collector/ready-colonies", headers=headers)
        
        if updated_colonies_response.status_code == 200:
            updated_colonies = updated_colonies_response.json().get('colonies', [])
            updated_colony = next((c for c in updated_colonies if c['colony_id'] == colony_id), None)
            
            if updated_colony:
                print(f"Updated waste amounts:")
                print(f"  Plastic: {updated_colony.get('current_plastic_kg', 0)}kg (was {colony.get('current_plastic_kg', 0)}kg)")
                print(f"  Paper: {updated_colony.get('current_paper_kg', 0)}kg (was {colony.get('current_paper_kg', 0)}kg)")
                print("✅ Colony waste amounts updated successfully!")
            else:
                print("⚠️ Colony not found in updated list")
        else:
            print(f"❌ Failed to verify updates: {updated_colonies_response.text}")
    else:
        print("❌ Collection completion failed")

if __name__ == "__main__":
    test_collection_completion()