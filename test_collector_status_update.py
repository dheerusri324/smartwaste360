#!/usr/bin/env python3
"""
Test collector status update functionality
"""

import requests

def test_collector_status_update():
    """Test updating collector status"""
    try:
        # Login as admin
        print("🔐 Logging in as admin...")
        login_data = {
            "email": "admin@gmail.com",
            "password": "admin"
        }
        
        login_response = requests.post(
            'https://smartwaste360-backend.onrender.com/api/admin/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.text}")
            return False
            
        access_token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Admin login successful!")
        
        # Get current collectors
        print("\n📋 Getting current collectors...")
        collectors_response = requests.get(
            'https://smartwaste360-backend.onrender.com/api/admin/collectors',
            headers=headers,
            timeout=10
        )
        
        if collectors_response.status_code != 200:
            print(f"❌ Failed to get collectors: {collectors_response.text}")
            return False
            
        collectors = collectors_response.json().get('collectors', [])
        print(f"✅ Found {len(collectors)} collectors")
        
        if not collectors:
            print("❌ No collectors to test with")
            return False
        
        # Test updating the first collector's status
        test_collector = collectors[0]
        collector_id = test_collector['collector_id']
        current_status = test_collector['is_active']
        new_status = not current_status
        
        print(f"\n🔄 Testing status update for '{test_collector['name']}'")
        print(f"   Current status: {current_status}")
        print(f"   New status: {new_status}")
        
        # Update collector status
        update_response = requests.put(
            f'https://smartwaste360-backend.onrender.com/api/admin/collectors/{collector_id}/status',
            json={'is_active': new_status},
            headers=headers,
            timeout=10
        )
        
        print(f"Update status: {update_response.status_code}")
        print(f"Update response: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ Status update successful!")
            
            # Verify the change by getting collectors again
            print("\n🔍 Verifying the change...")
            verify_response = requests.get(
                'https://smartwaste360-backend.onrender.com/api/admin/collectors',
                headers=headers,
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_collectors = verify_response.json().get('collectors', [])
                updated_collector = next((c for c in updated_collectors if c['collector_id'] == collector_id), None)
                
                if updated_collector and updated_collector['is_active'] == new_status:
                    print(f"✅ Status change verified! '{updated_collector['name']}' is now {'active' if new_status else 'inactive'}")
                    return True
                else:
                    print("❌ Status change not reflected in database")
                    return False
            else:
                print(f"❌ Failed to verify change: {verify_response.text}")
                return False
        else:
            print(f"❌ Status update failed: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Collector Status Update...")
    print("=" * 50)
    
    success = test_collector_status_update()
    
    if success:
        print("\n🎉 Collector status update is working!")
        print("📱 The mobile admin panel should now persist collector status changes!")
    else:
        print("\n❌ Collector status update failed - needs debugging")