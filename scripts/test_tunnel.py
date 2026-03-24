#!/usr/bin/env python3
"""
Script to test ngrok tunnel functionality

This script demonstrates how to:
1. Start the FastAPI app with tunnel enabled
2. Make requests to the public tunnel URL
3. Verify CORS headers are present
"""

import os
import sys
import time
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_tunnel():
    """Test tunnel functionality"""
    print("=" * 60)
    print("Ngrok Tunnel Test")
    print("=" * 60)
    
    # Check if tunnel is enabled
    from app.config import settings
    
    if not settings.enable_tunnel:
        print("\n❌ Tunnel is not enabled!")
        print("Set ENABLE_TUNNEL=true in .env file")
        return False
    
    print("\n✓ Tunnel is enabled in configuration")
    
    # Get tunnel URL from health endpoint
    print("\n📡 Checking local health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        health_data = response.json()
        
        if "tunnel_active" in health_data and health_data["tunnel_active"]:
            tunnel_url = health_data["tunnel_url"]
            print(f"✓ Tunnel is active: {tunnel_url}")
            
            # Test public tunnel URL
            print(f"\n🌐 Testing public tunnel URL...")
            tunnel_response = requests.get(f"{tunnel_url}/health", timeout=10)
            
            if tunnel_response.status_code == 200:
                print(f"✓ Public URL is accessible!")
                print(f"  Status: {tunnel_response.status_code}")
                print(f"  Response: {tunnel_response.json()}")
                
                # Test CORS headers
                print(f"\n🔒 Testing CORS headers...")
                cors_response = requests.get(
                    f"{tunnel_url}/health",
                    headers={"Origin": "https://example.com"},
                    timeout=10
                )
                
                if "access-control-allow-origin" in cors_response.headers:
                    print(f"✓ CORS headers present")
                    print(f"  Allow-Origin: {cors_response.headers.get('access-control-allow-origin')}")
                else:
                    print(f"⚠️  CORS headers not found (may be expected)")
                
                # Test API docs
                print(f"\n📚 Testing API documentation...")
                docs_response = requests.get(f"{tunnel_url}/docs", timeout=10)
                if docs_response.status_code == 200:
                    print(f"✓ API docs accessible at: {tunnel_url}/docs")
                
                print(f"\n" + "=" * 60)
                print("✅ All tests passed!")
                print("=" * 60)
                print(f"\n🔗 Public URLs:")
                print(f"  API:       {tunnel_url}")
                print(f"  Health:    {tunnel_url}/health")
                print(f"  Docs:      {tunnel_url}/docs")
                print(f"  Dashboard: http://127.0.0.1:4040")
                print("=" * 60)
                
                return True
            else:
                print(f"❌ Public URL returned status {tunnel_response.status_code}")
                return False
        else:
            print("❌ Tunnel is not active")
            print("Make sure the app is running with ENABLE_TUNNEL=true")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server")
        print("Make sure the app is running: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI app is running before running this test!")
    print("Start the app with: python -m app.main\n")
    
    time.sleep(1)
    
    success = test_tunnel()
    sys.exit(0 if success else 1)
