#!/usr/bin/env python3
"""
Health Check Script for Telegram Bot
Can be used for external monitoring
"""

import requests
import sys
import json
from datetime import datetime

def check_health(base_url):
    """Check bot health status"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot is healthy")
            print(f"Status: {data.get('status')}")
            print(f"Bot Status: {data.get('bot_status')}")
            print(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def check_api(base_url, api_key):
    """Check API endpoints"""
    try:
        # Test user info endpoint
        test_data = {
            "api_key": api_key,
            "user_id": "123456789"  # Test user ID
        }
        
        response = requests.post(
            f"{base_url}/api/userinfo",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API endpoints accessible")
            return True
        else:
            print(f"❌ API check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API check error: {e}")
        return False

def main():
    """Main health check function"""
    if len(sys.argv) < 2:
        print("Usage: python health_check.py <base_url> [api_key]")
        print("Example: python health_check.py https://your-app.onrender.com your_api_key")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 Checking bot health at {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Check basic health
    health_ok = check_health(base_url)
    
    # Check API if key provided
    api_ok = True
    if api_key:
        api_ok = check_api(base_url, api_key)
    
    print("-" * 50)
    
    if health_ok and api_ok:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("💥 Some checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
