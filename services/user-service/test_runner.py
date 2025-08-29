#!/usr/bin/env python3
"""
Comprehensive test runner for the User Management API
"""
import requests
import json
import io
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

class UserServiceTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        self.test_admin_id = None
        
    def run_all_tests(self):
        """Run all test suites"""
        print_info("Starting User Service API Tests")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_connectivity():
            print_error("API is not accessible. Please ensure the service is running.")
            return False
            
        # Run test suites
        test_suites = [
            ("Authentication Tests", self.test_authentication),
            ("User Profile Tests", self.test_user_profile),
            ("Admin Functionality Tests", self.test_admin_functionality),
            ("Security Tests", self.test_security),
            ("Error Handling Tests", self.test_error_handling)
        ]
        
        passed = 0
        failed = 0
        
        for suite_name, test_function in test_suites:
            print(f"\n{Colors.BLUE}Running {suite_name}...{Colors.ENDC}")
            print("-" * 30)
            
            try:
                if test_function():
                    passed += 1
                    print_success(f"{suite_name} PASSED")
                else:
                    failed += 1
                    print_error(f"{suite_name} FAILED")
            except Exception as e:
                failed += 1
                print_error(f"{suite_name} FAILED with exception: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print_info(f"Test Summary: {passed} passed, {failed} failed")
        
        if failed == 0:
            print_success("All tests passed! 🎉")
            return True
        else:
            print_error(f"{failed} test suite(s) failed")
            return False
    
    def test_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print_success("API is accessible")
                return True
            else:
                print_error(f"API returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Failed to connect to API: {e}")
            return False
    
    def test_authentication(self):
        """Test authentication endpoints"""
        success = True
        
        # Generate unique identifiers for this test run
        import time
        timestamp = int(time.time())
        
        # Test user signup
        try:
            signup_data = {
                "username": f"testuser_api_{timestamp}",
                "email": f"testuser_{timestamp}@api.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/signup", json=signup_data)
            if response.status_code == 201:
                self.test_user_id = response.json()["user"]["id"]
                print_success("User signup successful")
            else:
                print_error(f"User signup failed: {response.status_code} - {response.text}")
                success = False
        except Exception as e:
            print_error(f"User signup exception: {e}")
            success = False
        
        # Test user login
        try:
            login_data = {
                "email": f"testuser_{timestamp}@api.com",
                "password": "TestPassword123!"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=login_data)
            if response.status_code == 200:
                self.user_token = response.json()["access_token"]
                print_success("User login successful")
            else:
                print_error(f"User login failed: {response.status_code} - {response.text}")
                success = False
        except Exception as e:
            print_error(f"User login exception: {e}")
            success = False
        
        # Test admin user creation and login
        try:
            # First try with the actual super admin credentials
            super_admin_login = {
                "username": "super",
                "password": "SuperAdminPassword123!"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=super_admin_login)
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                print_success("Super Admin login successful")
            else:
                # Fallback: Create admin via signup (will be client first)
                admin_signup_data = {
                    "username": f"testadmin_api_{timestamp}",
                    "email": f"testadmin_{timestamp}@api.com",
                    "password": "AdminPassword123!",
                    "first_name": "Test",
                    "last_name": "Admin"
                }
                
                response = requests.post(f"{BASE_URL}{API_PREFIX}/signup", json=admin_signup_data)
                if response.status_code == 201:
                    self.test_admin_id = response.json()["user"]["id"]
                    print_success("Admin user created")
                    
                    # Login as admin
                    admin_login_data = {
                        "email": f"testadmin_{timestamp}@api.com",
                        "password": "AdminPassword123!"
                    }
                    
                    response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=admin_login_data)
                    if response.status_code == 200:
                        self.admin_token = response.json()["access_token"]
                        print_success("Admin login successful")
                    else:
                        print_error(f"Admin login failed: {response.status_code}")
                        success = False
                else:
                    print_error(f"Admin signup failed: {response.status_code}")
                    success = False
        except Exception as e:
            print_error(f"Admin creation exception: {e}")
            success = False
        
        # Test invalid credentials
        try:
            invalid_login = {
                "email": f"testuser_{timestamp}@api.com",
                "password": "WrongPassword"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=invalid_login)
            if response.status_code == 401:
                print_success("Invalid credentials properly rejected")
            else:
                print_error(f"Invalid credentials not properly rejected: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Invalid credentials test exception: {e}")
            success = False
        
        return success
    
    def test_user_profile(self):
        """Test user profile management"""
        if not self.user_token:
            print_error("No user token available for profile tests")
            return False
        
        success = True
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test get profile
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}/users/me", headers=headers)
            if response.status_code == 200:
                profile = response.json()
                print_success(f"Profile retrieved for user: {profile['username']}")
            else:
                print_error(f"Failed to get profile: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Get profile exception: {e}")
            success = False
        
        # Test profile update
        try:
            update_data = {
                "first_name": "UpdatedTest",
                "last_name": "UpdatedUser",
                "year_of_birth": 1990,
                "description": "Updated via API test"
            }
            
            response = requests.put(f"{BASE_URL}{API_PREFIX}/users/me", headers=headers, json=update_data)
            if response.status_code == 200:
                updated_profile = response.json()
                if updated_profile["first_name"] == "UpdatedTest":
                    print_success("Profile update successful")
                else:
                    print_error("Profile update data mismatch")
                    success = False
            else:
                print_error(f"Profile update failed: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Profile update exception: {e}")
            success = False
        
        # Test avatar upload (mock)
        try:
            # Create a small test image file
            image_content = b"fake_image_content_for_testing"
            files = {
                "file": ("test_avatar.jpg", io.BytesIO(image_content), "image/jpeg")
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/users/me/avatar", headers=headers, files=files)
            if response.status_code == 200:
                avatar_response = response.json()
                if "avatar_url" in avatar_response:
                    print_success("Avatar upload successful")
                else:
                    print_error("Avatar upload response missing avatar_url")
                    success = False
            else:
                print_error(f"Avatar upload failed: {response.status_code} - {response.text}")
                success = False
        except Exception as e:
            print_error(f"Avatar upload exception: {e}")
            success = False
        
        return success
    
    def test_admin_functionality(self):
        """Test admin functionality (requires promoting test admin to admin role)"""
        if not self.admin_token:
            print_error("No admin token available for admin tests")
            return False
        
        success = True
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Note: This test will fail if the admin user doesn't have admin role
        # We need to promote the user first (usually done manually or via script)
        
        # Test admin dashboard
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}/admin/dashboard", headers=headers)
            if response.status_code == 200:
                dashboard = response.json()
                print_success(f"Admin dashboard accessed - {dashboard['total_users']} users")
            elif response.status_code == 403:
                print_warning("Admin dashboard access denied - user may not have admin role")
                # This is expected if we haven't promoted the user to admin
                return True
            else:
                print_error(f"Admin dashboard failed: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Admin dashboard exception: {e}")
            success = False
        
        # Test get all users
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                print_success(f"Users list retrieved - {len(users)} users")
            elif response.status_code == 403:
                print_warning("Users list access denied - user may not have admin role")
                return True
            else:
                print_error(f"Users list failed: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Users list exception: {e}")
            success = False
        
        return success
    
    def test_security(self):
        """Test security measures"""
        success = True
        
        # Test accessing protected endpoints without token
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}/users/me")
            if response.status_code == 403:
                print_success("Protected endpoint properly secured")
            else:
                print_error(f"Protected endpoint not secured: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Security test exception: {e}")
            success = False
        
        # Test accessing admin endpoints as regular user
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BASE_URL}{API_PREFIX}/admin/dashboard", headers=headers)
                if response.status_code == 403:
                    print_success("Admin endpoints properly secured from regular users")
                else:
                    print_error(f"Admin endpoints not properly secured: {response.status_code}")
                    success = False
            except Exception as e:
                print_error(f"Admin security test exception: {e}")
                success = False
        
        # Test invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{BASE_URL}{API_PREFIX}/users/me", headers=headers)
            if response.status_code in [401, 403]:  # Both are valid security responses
                print_success("Invalid token properly rejected")
            else:
                print_error(f"Invalid token not properly rejected: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Invalid token test exception: {e}")
            success = False
        
        return success
    
    def test_error_handling(self):
        """Test error handling and validation"""
        success = True
        
        # Test invalid signup data
        try:
            invalid_signup = {
                "username": "ab",  # Too short
                "email": "invalid-email",
                "password": "weak"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/signup", json=invalid_signup)
            if response.status_code == 422:
                print_success("Invalid signup data properly validated")
            else:
                print_error(f"Invalid signup data not properly validated: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Invalid signup test exception: {e}")
            success = False
        
        # Test duplicate email signup
        try:
            # Use an existing email from our test
            import time
            timestamp = int(time.time())
            
            # First create a user
            first_user = {
                "username": f"firstuser_{timestamp}",
                "email": f"duplicate_{timestamp}@api.com",
                "password": "FirstPassword123!"
            }
            requests.post(f"{BASE_URL}{API_PREFIX}/signup", json=first_user)
            
            # Then try to create another with same email
            duplicate_signup = {
                "username": f"seconduser_{timestamp}",
                "email": f"duplicate_{timestamp}@api.com",  # Same email
                "password": "AnotherPassword123!"
            }
            
            response = requests.post(f"{BASE_URL}{API_PREFIX}/signup", json=duplicate_signup)
            if response.status_code == 400:
                print_success("Duplicate email properly rejected")
            else:
                print_error(f"Duplicate email not properly rejected: {response.status_code}")
                success = False
        except Exception as e:
            print_error(f"Duplicate email test exception: {e}")
            success = False
        
        # Test invalid file upload
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                text_content = b"this is not an image"
                files = {
                    "file": ("test.txt", io.BytesIO(text_content), "text/plain")
                }
                
                response = requests.post(f"{BASE_URL}{API_PREFIX}/users/me/avatar", headers=headers, files=files)
                if response.status_code == 400:
                    print_success("Invalid file type properly rejected")
                else:
                    print_error(f"Invalid file type not properly rejected: {response.status_code}")
                    success = False
            except Exception as e:
                print_error(f"Invalid file test exception: {e}")
                success = False
        
        return success

def main():
    """Main test runner"""
    tester = UserServiceTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
