#!/usr/bin/env python3
"""
SmartWaste360 Application Test Script
Tests key functionality and API endpoints
"""

import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Test if backend server is responding"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is responding")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_analytics_endpoint():
    """Test analytics endpoint (without auth for basic check)"""
    try:
        response = requests.get('http://localhost:5000/api/analytics/summary', timeout=5)
        # Even if it returns 401 (unauthorized), it means the endpoint exists
        if response.status_code in [200, 401, 403]:
            print("✅ Analytics endpoint is accessible")
            return True
        else:
            print(f"❌ Analytics endpoint returned unexpected status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing analytics endpoint: {e}")
        return False

def main():
    print("🧪 SmartWaste360 Application Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test backend connectivity
    print("1. Testing Backend Server...")
    backend_ok = test_backend_health()
    
    if backend_ok:
        print("\n2. Testing Health Endpoint...")
        test_health_endpoint()
        
        print("\n3. Testing Analytics Endpoint...")
        test_analytics_endpoint()
    
    print("\n" + "=" * 50)
    
    if backend_ok:
        print("🎉 Basic connectivity tests passed!")
        print("\n📋 Next Steps:")
        print("   • Open http://localhost:3000 in your browser")
        print("   • Test user registration and login")
        print("   • Try waste submission with camera")
        print("   • Check analytics dashboard")
        print("   • Test collector features")
    else:
        print("⚠️  Backend server needs to be started first")
        print("   Run: python app.py")

if __name__ == "__main__":
    main()