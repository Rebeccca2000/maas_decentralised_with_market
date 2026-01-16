#!/usr/bin/env python3
"""
Test script to verify blockchain frontend functionality
"""

import requests
import json
import time

def test_blockchain_status():
    """Test blockchain status endpoint"""
    print("🔍 Testing blockchain status...")
    try:
        response = requests.get("http://localhost:5000/api/blockchain/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Blockchain Status: {data}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_contracts_endpoint():
    """Test contracts endpoint"""
    print("\n🔍 Testing contracts endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/blockchain/contracts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contracts Data: {json.dumps(data, indent=2)}")
            
            # Check for problematic fields
            problematic_fields = []
            for key, value in data.items():
                if not isinstance(value, str) or not value.startswith('0x') or len(value) != 42:
                    if key not in ['network', 'timestamp', 'deployer']:
                        problematic_fields.append(f"{key}: {value} (type: {type(value)})")
            
            if problematic_fields:
                print(f"⚠️  Problematic fields found: {problematic_fields}")
            else:
                print("✅ All contract addresses look valid")
            
            return True
        else:
            print(f"❌ Contracts check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_web_interface():
    """Test web interface accessibility"""
    print("\n🔍 Testing web interface...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print(f"✅ Web interface accessible (Content length: {len(response.content)} bytes)")
            return True
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing Blockchain Frontend Functionality")
    print("=" * 60)
    
    tests = [
        ("Backend API", test_blockchain_status),
        ("Contracts Endpoint", test_contracts_endpoint),
        ("Web Interface", test_web_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend should be working correctly.")
        print("\n💡 If you're still seeing errors in the browser:")
        print("   1. Clear browser cache and refresh")
        print("   2. Check browser console for any remaining errors")
        print("   3. Try opening http://localhost:3000 in an incognito window")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
