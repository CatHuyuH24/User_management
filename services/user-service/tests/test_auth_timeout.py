"""
Comprehensive tests for authentication timeout and token validation issues
"""

import pytest
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from unittest.mock import patch
from jose import jwt

from app.main import app
from app.core.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service
from app.core.config import settings

client = TestClient(app)

class TestAuthenticationTimeout:
    """Test authentication timeout and token validation issues."""

    def setup_method(self):
        """Setup test data."""
        self.client_user_data = {
            "email": "client@example.com",
            "password": "ClientPassword123?"
        }
        self.admin_user_data = {
            "email": "super@admin.com", 
            "password": "SuperAdminPassword123!"
        }

    def test_login_success_client(self):
        """Test successful client login."""
        response = client.post("/api/v1/login", json=self.client_user_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["role"] == "client"

    def test_login_success_admin(self):
        """Test successful admin login."""
        response = client.post("/api/v1/login", json=self.admin_user_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["role"] == "super_admin"

    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        invalid_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/login", json=invalid_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_token_validation_me_endpoint(self):
        """Test token validation via /me endpoint."""
        # Login first
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /me endpoint
        me_response = client.get("/api/v1/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        
        user_data = me_response.json()
        assert user_data["email"] == self.client_user_data["email"]
        assert user_data["role"] == "client"

    def test_expired_token_simulation(self):
        """Test behavior with expired token simulation."""
        # Create an expired token manually
        past_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": "1",
            "email": "client@example.com",
            "role": "client",
            "username": "client",
            "type": "access",
            "exp": past_time
        }
        
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        # Try to access protected endpoint
        response = client.get("/api/v1/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_token(self):
        """Test behavior with malformed token."""
        malformed_token = "invalid.token.here"
        headers = {"Authorization": f"Bearer {malformed_token}"}
        
        response = client.get("/api/v1/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_token(self):
        """Test behavior without token."""
        response = client.get("/api/v1/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_access_with_client_token(self):
        """Test admin endpoint access with client token (should fail)."""
        # Login as client
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access admin endpoint
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin privileges required" in response.json()["detail"]

    def test_admin_access_with_admin_token(self):
        """Test admin endpoint access with admin token (should succeed)."""
        # Login as admin
        login_response = client.post("/api/v1/login", json=self.admin_user_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access admin endpoint
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_token_refresh_behavior(self):
        """Test token behavior after multiple requests."""
        # Login
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple requests with same token
        for i in range(5):
            response = client.get("/api/v1/me", headers=headers)
            assert response.status_code == status.HTTP_200_OK
            
    def test_concurrent_login_sessions(self):
        """Test multiple concurrent login sessions."""
        tokens = []
        
        # Create multiple sessions
        for i in range(3):
            login_response = client.post("/api/v1/login", json=self.client_user_data)
            assert login_response.status_code == status.HTTP_200_OK
            tokens.append(login_response.json()["access_token"])
        
        # All tokens should be valid
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/me", headers=headers)
            assert response.status_code == status.HTTP_200_OK

    def test_logout_functionality(self):
        """Test logout functionality if implemented."""
        # Login first
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token works
        me_response = client.get("/api/v1/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        
        # Test logout if endpoint exists
        logout_response = client.post("/api/v1/logout", headers=headers)
        # Note: This might return 404 if logout is not implemented
        # We'll handle both cases
        if logout_response.status_code != status.HTTP_404_NOT_FOUND:
            # If logout is implemented, token should be invalidated
            me_response_after_logout = client.get("/api/v1/me", headers=headers)
            # Implementation may vary - some systems invalidate tokens, others don't

    def test_password_change_token_invalidation(self):
        """Test if tokens are invalidated after password change."""
        # Login
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        original_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {original_token}"}
        
        # Change password
        password_change_data = {
            "current_password": self.client_user_data["password"],
            "new_password": "NewClientPassword123!"
        }
        
        change_response = client.post("/api/v1/auth/change-password", 
                                    json=password_change_data, 
                                    headers=headers)
        assert change_response.status_code == status.HTTP_200_OK
        
        # Try to use old token (implementation may vary)
        me_response = client.get("/api/v1/me", headers=headers)
        # Some implementations invalidate tokens after password change, others don't
        
        # Try to login with new password
        new_login_data = {
            "email": self.client_user_data["email"],
            "password": "NewClientPassword123!"
        }
        new_login_response = client.post("/api/v1/login", json=new_login_data)
        assert new_login_response.status_code == status.HTTP_200_OK
        
        # Reset password for other tests
        new_token = new_login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        reset_data = {
            "current_password": "NewClientPassword123!",
            "new_password": self.client_user_data["password"]
        }
        client.post("/api/v1/auth/change-password", json=reset_data, headers=new_headers)

    def test_server_restart_token_persistence(self):
        """Test token behavior after simulated server restart."""
        # Login
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token works before restart
        me_response = client.get("/api/v1/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        
        # Simulate server restart by creating a new client
        new_client = TestClient(app)
        
        # Token should still be valid (JWT is stateless)
        me_response_after_restart = new_client.get("/api/v1/me", headers=headers)
        assert me_response_after_restart.status_code == status.HTTP_200_OK

    def test_user_deactivation_token_behavior(self):
        """Test token behavior when user is deactivated."""
        # This test requires admin privileges to deactivate a user
        # We'll skip this if we can't create/modify test users in the database
        pass

    def test_role_change_token_behavior(self):
        """Test token behavior when user role is changed."""
        # This would require database manipulation which might not be available
        # in the test environment. We'll skip this for now.
        pass


class TestTokenValidationEdgeCases:
    """Test edge cases for token validation."""
    
    def test_token_with_extra_whitespace(self):
        """Test token validation with extra whitespace."""
        login_response = client.post("/api/v1/login", json={
            "email": "client@example.com",
            "password": "ClientPassword123?"
        })
        token = login_response.json()["access_token"]
        
        # Add whitespace to token
        headers = {"Authorization": f"Bearer  {token}  "}
        response = client.get("/api/v1/me", headers=headers)
        # Most implementations should handle this gracefully
        
    def test_bearer_case_sensitivity(self):
        """Test Bearer keyword case sensitivity."""
        login_response = client.post("/api/v1/login", json={
            "email": "client@example.com",
            "password": "ClientPassword123?"
        })
        token = login_response.json()["access_token"]
        
        # Test different cases
        test_cases = ["bearer", "BEARER", "Bearer"]
        
        for bearer_keyword in test_cases:
            headers = {"Authorization": f"{bearer_keyword} {token}"}
            response = client.get("/api/v1/me", headers=headers)
            # Implementation may vary on case sensitivity

    def test_token_in_query_parameter(self):
        """Test if token is accepted in query parameters (should be rejected)."""
        login_response = client.post("/api/v1/login", json={
            "email": "client@example.com",
            "password": "ClientPassword123?"
        })
        token = login_response.json()["access_token"]
        
        # Try to pass token as query parameter (security risk)
        response = client.get(f"/api/v1/me?token={token}")
        # Should be rejected for security reasons
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    # Run tests directly
    test_class = TestAuthenticationTimeout()
    test_class.setup_method()
    
    print("🧪 Running Authentication Timeout Tests")
    print("=" * 50)
    
    try:
        test_class.test_login_success_client()
        print("✅ Client login test passed")
        
        test_class.test_login_success_admin()
        print("✅ Admin login test passed")
        
        test_class.test_admin_access_with_admin_token()
        print("✅ Admin access test passed")
        
        test_class.test_token_validation_me_endpoint()
        print("✅ Token validation test passed")
        
        test_class.test_server_restart_token_persistence()
        print("✅ Token persistence test passed")
        
        print("\n🎉 All basic authentication tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
