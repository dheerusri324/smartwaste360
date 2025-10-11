#!/usr/bin/env python3
"""
Check deployment status of SmartWaste360
"""

import requests
import json
from datetime import datetime

def check_backend():
    """Check backend deployment status"""
    try:
        response = requests.get('https://smartwaste360backend-production.up.railway.app/', timeout=10)
        data = response.json()
        
        print("🔧 Backend Status:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        # Check if new version is deployed
        if 'version' in data:
            print("   ✅ New version deployed!")
        else:
            print("   ⏳ Old version still running (deployment in progress)")
            
        return 'version' in data
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_frontend():
    """Check frontend deployment status"""
    try:
        response = requests.get('https://smartwaste360-frontend-kspryj8da-121012dheeraj-8860s-projects.vercel.app/', timeout=10)
        
        print("⚡ Frontend Status:")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.text)} bytes")
        
        # Check if it's loading properly
        if response.status_code == 200 and len(response.text) > 1000:
            print("   ✅ Frontend is accessible")
            return True
        else:
            print("   ⏳ Frontend deployment in progress")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🧪 SmartWaste360 Deployment Status Check")
    print("=" * 50)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    backend_ok = check_backend()
    print()
    frontend_ok = check_frontend()
    
    print()
    print("=" * 50)
    
    if backend_ok and frontend_ok:
        print("🎉 Both deployments successful!")
    elif backend_ok:
        print("🔧 Backend deployed, frontend still deploying...")
    elif frontend_ok:
        print("⚡ Frontend deployed, backend still deploying...")
    else:
        print("⏳ Both deployments still in progress...")
    
    print()
    print("📋 Manual Check URLs:")
    print("   Backend: https://smartwaste360backend-production.up.railway.app/")
    print("   Frontend: https://smartwaste360-frontend-kspryj8da-121012dheeraj-8860s-projects.vercel.app/")
    print("   GitHub Actions: https://github.com/dheerusri324/smartwaste360/actions")

if __name__ == "__main__":
    main()