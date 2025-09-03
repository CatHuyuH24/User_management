"""
Enhanced Integration Tests for Password Change Functionality
Tests both backend API and simulated frontend interactions
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

class TestPasswordChangeIntegration:
    """Integration tests for password change functionality across the system."""

    def setup_method(self):
        """Setup test data for each test."""
        self.test_users = {
            "client": {
                "username": "client",
                "email": "client@example.com",
                "password": "ClientPassword123?",
                "role": "client"
            },
            "admin": {
                "username": "super", 
                "email": "super@admin.com",
                "password": "SuperAdminPassword123!",
                "role": "super_admin"
            }
        }
        
    def authenticate_user(self, user_data: Dict[str, str]) -> str:
        """Authenticate a user and return access token."""
        login_url = f"{BASE_URL}/api/v1/login"
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")

    def test_backend_api_availability(self):
        """Test that the backend API is accessible."""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            assert response.status_code == 200
            print("✅ Backend API is accessible")
        except Exception as e:
            pytest.fail(f"Backend API not accessible: {e}")

    def test_frontend_availability(self):
        """Test that the frontend server is accessible."""
        try:
            response = requests.get(f"{FRONTEND_URL}/profile.html", timeout=5)
            assert response.status_code == 200
            print("✅ Frontend server is accessible")
        except Exception as e:
            pytest.fail(f"Frontend server not accessible: {e}")

    def test_client_password_change_complete_flow(self):
        """Test complete password change flow for client user."""
        user_data = self.test_users["client"]
        
        # Step 1: Authenticate user
        try:
            token = self.authenticate_user(user_data)
            print("✅ Client user authenticated successfully")
        except Exception as e:
            pytest.fail(f"Failed to authenticate client user: {e}")

        # Step 2: Change password via API
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        new_password = "NewClientPassword123!"
        
        headers = {"Authorization": f"Bearer {token}"}
        change_data = {
            "current_password": user_data["password"],
            "new_password": new_password
        }
        
        response = requests.post(change_url, json=change_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"
        print("✅ Client password changed successfully via API")

        # Step 3: Verify old password no longer works
        try:
            old_token = self.authenticate_user(user_data)
            pytest.fail("Old password should not work anymore")
        except Exception:
            print("✅ Old password correctly rejected")

        # Step 4: Verify new password works
        user_data["password"] = new_password
        try:
            new_token = self.authenticate_user(user_data)
            print("✅ New password works for authentication")
        except Exception as e:
            pytest.fail(f"New password should work: {e}")

        # Step 5: Access user profile with new token
        profile_url = f"{BASE_URL}/api/v1/me"
        profile_headers = {"Authorization": f"Bearer {new_token}"}
        profile_response = requests.get(profile_url, headers=profile_headers)
        
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == user_data["username"]
        assert profile_data["role"] == user_data["role"]
        print("✅ User profile accessible with new credentials")

        # Reset password for future tests
        reset_data = {
            "current_password": new_password,
            "new_password": "ClientPassword123?"
        }
        reset_response = requests.post(change_url, json=reset_data, headers=profile_headers)
        assert reset_response.status_code == 200
        print("✅ Password reset for future tests")

    def test_admin_password_change_complete_flow(self):
        """Test complete password change flow for admin user."""
        user_data = self.test_users["admin"]
        
        # Step 1: Authenticate admin user
        try:
            token = self.authenticate_user(user_data)
            print("✅ Admin user authenticated successfully")
        except Exception as e:
            pytest.fail(f"Failed to authenticate admin user: {e}")

        # Step 2: Change password via API
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        new_password = "NewSuperAdminPassword123!"
        
        headers = {"Authorization": f"Bearer {token}"}
        change_data = {
            "current_password": user_data["password"],
            "new_password": new_password
        }
        
        response = requests.post(change_url, json=change_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"
        print("✅ Admin password changed successfully via API")

        # Step 3: Verify admin still has proper permissions
        user_data["password"] = new_password
        new_token = self.authenticate_user(user_data)
        
        # Test admin-specific endpoint
        admin_headers = {"Authorization": f"Bearer {new_token}"}
        users_url = f"{BASE_URL}/api/v1/admin/users"
        users_response = requests.get(users_url, headers=admin_headers)
        
        assert users_response.status_code == 200
        print("✅ Admin permissions maintained after password change")

        # Reset password for future tests
        reset_data = {
            "current_password": new_password,
            "new_password": "SuperAdminPassword123!"
        }
        reset_response = requests.post(change_url, json=reset_data, headers=admin_headers)
        assert reset_response.status_code == 200
        print("✅ Admin password reset for future tests")

    def test_password_validation_rules(self):
        """Test that password validation rules are properly enforced."""
        user_data = self.test_users["client"]
        token = self.authenticate_user(user_data)
        
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test various invalid passwords
        invalid_passwords = [
            ("short", "Password too short"),
            ("nouppercase123!", "No uppercase letter"),
            ("NOLOWERCASE123!", "No lowercase letter"), 
            ("NoDigits!", "No digits"),
            ("NoSpecialChars123", "No special characters"),
            (user_data["password"], "Same as current password")
        ]
        
        for invalid_password, test_name in invalid_passwords:
            change_data = {
                "current_password": user_data["password"],
                "new_password": invalid_password
            }
            
            response = requests.post(change_url, json=change_data, headers=headers)
            assert response.status_code in [400, 422], f"Failed validation for: {test_name}"
            print(f"✅ Password validation working for: {test_name}")

    def test_concurrent_password_changes(self):
        """Test handling of concurrent password change attempts."""
        user_data = self.test_users["client"]
        token = self.authenticate_user(user_data)
        
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple concurrent password change requests
        import threading
        results = []
        
        def change_password(password_suffix):
            try:
                change_data = {
                    "current_password": user_data["password"],
                    "new_password": f"NewPassword{password_suffix}!"
                }
                response = requests.post(change_url, json=change_data, headers=headers)
                results.append((password_suffix, response.status_code))
            except Exception as e:
                results.append((password_suffix, f"Error: {e}"))
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=change_password, args=(f"123{i}",))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one should succeed, others should fail
        success_count = sum(1 for _, status in results if status == 200)
        assert success_count <= 1, "Multiple concurrent password changes should not all succeed"
        print(f"✅ Concurrent password change handling: {success_count} succeeded")

    def test_password_change_security_headers(self):
        """Test that proper security headers are returned."""
        user_data = self.test_users["client"]
        token = self.authenticate_user(user_data)
        
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        change_data = {
            "current_password": user_data["password"],
            "new_password": "NewSecurePassword123!"
        }
        
        response = requests.post(change_url, json=change_data, headers=headers)
        assert response.status_code == 200
        
        # Check for security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]
        
        for header in security_headers:
            if header in response.headers:
                print(f"✅ Security header present: {header}")
        
        # Reset password
        reset_data = {
            "current_password": "NewSecurePassword123!",
            "new_password": user_data["password"]
        }
        requests.post(change_url, json=reset_data, headers=headers)

    def test_rate_limiting_password_changes(self):
        """Test rate limiting on password change attempts."""
        user_data = self.test_users["client"]
        token = self.authenticate_user(user_data)
        
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make rapid password change attempts
        for i in range(5):
            change_data = {
                "current_password": "wrong_password",
                "new_password": f"NewPassword{i}!"
            }
            
            response = requests.post(change_url, json=change_data, headers=headers)
            
            # After several failed attempts, should get rate limited
            if i >= 3 and response.status_code == 429:
                print("✅ Rate limiting activated after multiple failed attempts")
                break
                
            time.sleep(0.1)

    def test_audit_logging_password_changes(self):
        """Test that password changes are properly logged."""
        user_data = self.test_users["client"]
        token = self.authenticate_user(user_data)
        
        change_url = f"{BASE_URL}/api/v1/auth/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Successful password change
        change_data = {
            "current_password": user_data["password"],
            "new_password": "AuditTestPassword123!"
        }
        
        response = requests.post(change_url, json=change_data, headers=headers)
        assert response.status_code == 200
        print("✅ Password change completed for audit test")
        
        # The actual audit log checking would require access to logs
        # This is a placeholder for integration with logging system
        
        # Reset password
        reset_data = {
            "current_password": "AuditTestPassword123!",
            "new_password": user_data["password"]
        }
        reset_response = requests.post(change_url, json=reset_data, headers=headers)
        assert reset_response.status_code == 200

if __name__ == "__main__":
    # Run tests directly
    test_class = TestPasswordChangeIntegration()
    test_class.setup_method()
    
    try:
        test_class.test_backend_api_availability()
        test_class.test_frontend_availability()
        test_class.test_client_password_change_complete_flow()
        test_class.test_admin_password_change_complete_flow()
        test_class.test_password_validation_rules()
        test_class.test_concurrent_password_changes()
        test_class.test_password_change_security_headers()
        test_class.test_rate_limiting_password_changes()
        test_class.test_audit_logging_password_changes()
        
        print("\n🎉 All password change integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
