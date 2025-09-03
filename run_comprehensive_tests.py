#!/usr/bin/env python3
"""
Comprehensive Test Runner for Password Change Functionality
Runs all password-related tests and generates a report
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
    def run_test(self, test_name, command, working_dir=None):
        """Run a single test and capture results."""
        print(f"\n🧪 Running {test_name}...")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            if working_dir:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    cwd=working_dir,
                    timeout=300  # 5 minute timeout
                )
            else:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = "PASSED"
                self.results["summary"]["passed"] += 1
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
            else:
                status = "FAILED"
                self.results["summary"]["failed"] += 1
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            
            self.results["tests"][test_name] = {
                "status": status,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            status = "TIMEOUT"
            self.results["summary"]["failed"] += 1
            print(f"⏰ {test_name} TIMED OUT ({duration:.2f}s)")
            
            self.results["tests"][test_name] = {
                "status": status,
                "duration": duration,
                "stdout": "Test timed out",
                "stderr": "Test execution exceeded timeout limit",
                "return_code": -1
            }
            
        except Exception as e:
            duration = time.time() - start_time
            status = "ERROR"
            self.results["summary"]["failed"] += 1
            print(f"💥 {test_name} ERROR ({duration:.2f}s): {e}")
            
            self.results["tests"][test_name] = {
                "status": status,
                "duration": duration,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
        
        self.results["summary"]["total"] += 1
        
    def generate_report(self):
        """Generate test report."""
        print("\n" + "=" * 60)
        print("                   TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"] 
        failed = self.results["summary"]["failed"]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.results["tests"].items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"  {status_icon} {test_name}: {result['status']} ({result['duration']:.2f}s)")
            
            if result["status"] != "PASSED" and result["stderr"]:
                print(f"      Error: {result['stderr'][:100]}...")
        
        # Save detailed report to file
        report_file = "test_results.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed == total

def main():
    print("🚀 Starting Comprehensive Password Change Test Suite")
    print("=" * 60)
    
    runner = TestRunner()
    
    # Get the current directory
    current_dir = os.getcwd()
    user_service_dir = os.path.join(current_dir, "services", "user-service")
    
    # Check if we're in the right directory
    if not os.path.exists(user_service_dir):
        print("❌ Error: Cannot find user-service directory")
        print(f"Current directory: {current_dir}")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Test 1: Unit Tests for Password Change
    runner.run_test(
        "Password Change Unit Tests",
        "python -m pytest tests/test_password_change.py -v",
        user_service_dir
    )
    
    # Test 2: Integration Tests
    runner.run_test(
        "Password Change Integration Tests", 
        "python -m pytest tests/test_password_integration.py -v",
        user_service_dir
    )
    
    # Test 3: Authentication Tests
    runner.run_test(
        "Authentication Tests",
        "python -m pytest tests/test_auth.py -v",
        user_service_dir
    )
    
    # Test 4: User Service Tests
    runner.run_test(
        "User Service Tests",
        "python -m pytest tests/test_user_service.py -v", 
        user_service_dir
    )
    
    # Test 5: Admin Tests  
    runner.run_test(
        "Admin Tests",
        "python -m pytest tests/test_admin.py -v",
        user_service_dir
    )
    
    # Test 6: All Integration Tests
    runner.run_test(
        "Full Integration Test Suite",
        "python -m pytest tests/test_integration.py -v",
        user_service_dir
    )
    
    # Test 7: API Endpoint Tests
    runner.run_test(
        "API Endpoint Tests",
        "python test_endpoints.py",
        current_dir
    )
    
    # Generate and display final report
    success = runner.generate_report()
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
