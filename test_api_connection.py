#!/usr/bin/env python3
"""
Test API connection and login functionality
"""

import requests
import json

def test_backend_endpoints():
    """Test key backend endpoints"""
    base_url = "https://smartwaste360-backend.onrender.com"
    
    print("🔧 Testing Backend Endpoints")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test auth endpoints (should return method not allowed or similar)
    try:
        response = requests.get(f"{base_url}/api/auth/login", timeout=10)
        print(f"✅ Auth login endpoint accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth endpoint failed: {e}")
    
    # Test registration endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/register", timeout=10)
        print(f"✅ Auth register endpoint accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Register endpoint failed: {e}")

def test_cors():
    """Test CORS configuration"""
    print("\n🌐 Testing CORS Configuration")
    print("=" * 40)
    
    try:
        response = requests.options(
            "https://smartwaste360-backend.onrender.com/api/auth/login",
            headers={
                'Origin': 'https://smartwaste360-frontend-b9jirihyv-121012dheeraj-8860s-projects.vercel.app',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        print(f"✅ CORS preflight: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def main():
    print("🧪 SmartWaste360 API Connection Test")
    print("=" * 50)
    
    test_backend_endpoints()
    test_cors()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("   Backend URL: https://smartwaste360-backend.onrender.com")
    print("   Frontend URL: https://smartwaste360-frontend-b9jirihyv-121012dheeraj-8860s-projects.vercel.app")
    print("   API Base: https://smartwaste360-backend.onrender.com/api")

if __name__ == "__main__":
    main()