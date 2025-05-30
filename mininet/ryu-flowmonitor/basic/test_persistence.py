#!/usr/bin/env python3
"""
Test script to demonstrate process persistence
This shows how the web GUI now remembers running processes
"""

import time
import requests
import json

def test_persistence():
    """Test the persistence feature"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing SDN Web GUI Process Persistence")
    print("=" * 50)
    
    try:
        # Test 1: Check initial status
        print("1. Checking initial status...")
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Controller: {status['controller_status']}")
            print(f"   Network: {status['network_status']}")
        else:
            print("   ❌ Failed to get status")
            return
        
        # Test 2: Start controller
        print("\n2. Starting Ryu controller...")
        response = requests.get(f"{base_url}/start_controller")
        if response.status_code == 200:
            print("   ✅ Controller start command sent")
            time.sleep(2)  # Wait for startup
            
            # Check status
            response = requests.get(f"{base_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Status: {status['controller_status']}")
            
        # Test 3: Simulate page refresh by checking status again
        print("\n3. Simulating page refresh (checking persistence)...")
        for i in range(3):
            time.sleep(1)
            response = requests.get(f"{base_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Refresh {i+1}: Controller = {status['controller_status']}")
            
        print("\n✅ Persistence test completed!")
        print("💡 The controller status should remain 'running' even after refreshes")
        print("💡 This is because the web GUI now saves and restores process information")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web GUI. Make sure it's running at http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_persistence()
