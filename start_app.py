#!/usr/bin/env python3
"""
SmartWaste360 Application Startup Script
Starts both backend and frontend servers
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import flask_cors
        import flask_jwt_extended
        print("✅ Backend dependencies OK")
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Check if frontend dependencies exist
    frontend_path = Path("frontend/node_modules")
    if frontend_path.exists():
        print("✅ Frontend dependencies OK")
    else:
        print("❌ Frontend dependencies missing")
        print("   Run: cd frontend && npm install")
        return False
    
    return True

def start_backend():
    """Start the Flask backend server"""
    print("\n🚀 Starting Backend Server...")
    try:
        # Start backend in a new process
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's still running
        if backend_process.poll() is None:
            print("✅ Backend server started on http://localhost:5000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend server"""
    print("\n🚀 Starting Frontend Server...")
    try:
        # Change to frontend directory and start
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Frontend server starting on http://localhost:3000")
        print("   (This may take a moment to compile...)")
        return frontend_process
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    print("🎯 SmartWaste360 Application Launcher")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Cannot start application without backend")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    
    print("\n" + "=" * 50)
    print("🎉 SmartWaste360 is starting up!")
    print("\n📋 Application URLs:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend API: http://localhost:5000")
    print("   • API Health: http://localhost:5000/health")
    
    print("\n🔧 Development Commands:")
    print("   • Test API: python test_app.py")
    print("   • Stop servers: Press Ctrl+C")
    
    print("\n⏳ Waiting for servers to fully start...")
    print("   The frontend may take 30-60 seconds to compile")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if backend is still running
            if backend_process.poll() is not None:
                print("\n❌ Backend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend server stopped")
        
        print("👋 SmartWaste360 shutdown complete")

if __name__ == "__main__":
    main()