#!/usr/bin/env python3
"""
Comprehensive MaaS Platform Functionality Test
Tests all major components and functionalities of the decentralized MaaS platform.
"""

import requests
import json
import time
import sys
from datetime import datetime

class MaaSPlatformTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.web_url = "http://localhost:3000"
        self.blockchain_url = "http://127.0.0.1:8545"
        self.test_results = {}
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_backend_connection(self):
        """Test backend API connection"""
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Backend API is running and responsive")
                self.log(f"   Backend connected: {data.get('backend_connected')}")
                self.log(f"   Blockchain connected: {data.get('blockchain_connected')}")
                self.log(f"   Simulation running: {data.get('simulation_running')}")
                return True
            else:
                self.log(f"❌ Backend API returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend API connection failed: {e}", "ERROR")
            return False
            
    def test_blockchain_connection(self):
        """Test blockchain connection and status"""
        try:
            response = requests.get(f"{self.base_url}/api/blockchain/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Blockchain connection is working")
                self.log(f"   Network ID: {data.get('network_id')}")
                self.log(f"   Latest block: {data.get('latest_block')}")
                self.log(f"   Node URL: {data.get('node_url')}")
                return True
            else:
                self.log(f"❌ Blockchain status check failed with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Blockchain connection test failed: {e}", "ERROR")
            return False
            
    def test_smart_contracts(self):
        """Test smart contract deployment and accessibility"""
        try:
            response = requests.get(f"{self.base_url}/api/blockchain/contracts", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Smart contracts are deployed and accessible")
                contracts = ['registry', 'request', 'auction', 'facade']
                for contract in contracts:
                    if contract in data:
                        self.log(f"   {contract.capitalize()}: {data[contract]}")
                    else:
                        self.log(f"   ⚠️  {contract.capitalize()}: Not found")
                return True
            else:
                self.log(f"❌ Smart contracts check failed with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Smart contracts test failed: {e}", "ERROR")
            return False
            
    def test_analytics_api(self):
        """Test analytics and metrics API"""
        try:
            response = requests.get(f"{self.base_url}/api/analytics/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Analytics API is working")
                self.log(f"   Total agents: {data.get('total_agents')}")
                self.log(f"   Active requests: {data.get('active_requests')}")
                self.log(f"   Success rate: {data.get('success_rate')}%")
                self.log(f"   Blockchain transactions: {data.get('blockchain_transactions')}")
                return True
            else:
                self.log(f"❌ Analytics API failed with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Analytics API test failed: {e}", "ERROR")
            return False
            
    def test_simulation_api(self):
        """Test simulation start/stop functionality"""
        try:
            # Test simulation start
            config = {
                "steps": 5,
                "commuters": 3,
                "providers": 2,
                "debug": False,
                "no_plots": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/simulation/start",
                json=config,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Simulation API is working")
                self.log(f"   Simulation ID: {data.get('simulation_id')}")
                self.log(f"   Success: {data.get('success')}")
                
                # Wait a moment and check status
                time.sleep(2)
                status_response = requests.get(f"{self.base_url}/api/simulation/status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    self.log(f"   Current step: {status_data.get('status', {}).get('current_step', 'N/A')}")
                    self.log(f"   Progress: {status_data.get('status', {}).get('progress', 'N/A')}%")
                
                return True
            else:
                self.log(f"❌ Simulation API failed with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Simulation API test failed: {e}", "ERROR")
            return False
            
    def test_web_interface(self):
        """Test web interface accessibility"""
        try:
            response = requests.get(self.web_url, timeout=5)
            if response.status_code == 200:
                self.log("✅ Web interface is accessible")
                self.log(f"   Status: {response.status_code}")
                self.log(f"   Content length: {len(response.content)} bytes")
                return True
            else:
                self.log(f"❌ Web interface returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Web interface test failed: {e}", "ERROR")
            return False
            
    def run_all_tests(self):
        """Run all functionality tests"""
        self.log("🚀 Starting comprehensive MaaS platform functionality test")
        self.log("=" * 70)
        
        tests = [
            ("Backend API Connection", self.test_backend_connection),
            ("Blockchain Connection", self.test_blockchain_connection),
            ("Smart Contracts", self.test_smart_contracts),
            ("Analytics API", self.test_analytics_api),
            ("Simulation API", self.test_simulation_api),
            ("Web Interface", self.test_web_interface),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Testing: {test_name}")
            self.log("-" * 50)
            
            try:
                if test_func():
                    passed += 1
                    self.test_results[test_name] = "PASSED"
                else:
                    self.test_results[test_name] = "FAILED"
            except Exception as e:
                self.log(f"❌ Test {test_name} crashed: {e}", "ERROR")
                self.test_results[test_name] = "CRASHED"
        
        # Print summary
        self.log("\n" + "=" * 70)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 70)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASSED" else "❌"
            self.log(f"{status_icon} {test_name}: {result}")
        
        self.log(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! MaaS platform is fully functional!")
            return True
        else:
            self.log("⚠️  Some tests failed. Check the logs above for details.")
            return False

if __name__ == "__main__":
    tester = MaaSPlatformTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
