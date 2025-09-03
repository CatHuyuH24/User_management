import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.services.auth_service import auth_service

client = TestClient(app)

class TestPasswordChange:
    """Test cases for password change functionality."""

    def test_change_password_success(self, client, auth_headers, test_user, db_session):
        """Test successful password change."""
        new_password = "NewPassword123!"
        password_data = {
            "current_password": "Password123!",  # Original password from test_user
            "new_password": new_password
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password updated successfully"
        
        # Verify password was actually changed in database
        db_session.refresh(test_user)
        assert verify_password(new_password, test_user.hashed_password)

    def test_change_password_wrong_current_password(self, client, auth_headers):
        """Test password change with incorrect current password."""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Current password is incorrect" in response.json()["detail"]

    def test_change_password_same_as_current(self, client, auth_headers):
        """Test password change with same password as current."""
        password_data = {
            "current_password": "Password123!",
            "new_password": "Password123!"  # Same as current
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             headers=auth_headers, 
                             json=password_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "New password must be different from current password" in response.json()["detail"]

    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test password change with weak new password."""
        test_cases = [
            {
                "current_password": "Password123!",
                "new_password": "weak",
                "expected_error": "at least 8 characters"
            },
            {
                "current_password": "Password123!",
                "new_password": "nouppercase123!",
                "expected_error": "uppercase letter"
            },
            {
                "current_password": "Password123!",
                "new_password": "NOLOWERCASE123!",
                "expected_error": "lowercase letter"
            },
            {
                "current_password": "Password123!",
                "new_password": "NoDigits!",
                "expected_error": "digit"
            },
            {
                "current_password": "Password123!",
                "new_password": "NoSpecialChars123",
                "expected_error": "special character"
            }
        ]
        
        for test_case in test_cases:
            response = client.post("/api/v1/auth/change-password", 
                                 headers=auth_headers, 
                                 json=test_case)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_change_password_unauthenticated(self, client):
        """Test password change without authentication."""
        password_data = {
            "current_password": "Password123!",
            "new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/auth/change-password", json=password_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_missing_fields(self, client, auth_headers):
        """Test password change with missing required fields."""
        test_cases = [
            {},  # No fields
            {"current_password": "Password123!"},  # Missing new_password
            {"new_password": "NewPassword123!"}    # Missing current_password
        ]
        
        for password_data in test_cases:
            response = client.post("/api/v1/auth/change-password", 
                                 headers=auth_headers, 
                                 json=password_data)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_change_password_admin_user(self, client, admin_user, db_session):
        """Test password change for admin user."""
        # Create admin auth headers
        login_data = {"email": admin_user.email, "password": "AdminPass123!"}
        login_response = client.post("/api/v1/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {token}"}
        
        new_password = "NewAdminPass123!"
        password_data = {
            "current_password": "AdminPass123!",
            "new_password": new_password
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             headers=admin_headers, 
                             json=password_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password updated successfully"
        
        # Verify password was changed
        db_session.refresh(admin_user)
        assert verify_password(new_password, admin_user.hashed_password)

    def test_change_password_super_admin_user(self, client, super_admin_user, db_session):
        """Test password change for super admin user."""
        # Create super admin auth headers
        login_data = {"email": super_admin_user.email, "password": "SuperAdminPass123!"}
        login_response = client.post("/api/v1/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        super_admin_headers = {"Authorization": f"Bearer {token}"}
        
        new_password = "NewSuperAdminPass123!"
        password_data = {
            "current_password": "SuperAdminPass123!",
            "new_password": new_password
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             headers=super_admin_headers, 
                             json=password_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password updated successfully"
        
        # Verify password was changed
        db_session.refresh(super_admin_user)
        assert verify_password(new_password, super_admin_user.hashed_password)

    def test_login_after_password_change(self, client, test_user, auth_headers, db_session):
        """Test that user can login with new password after change."""
        new_password = "NewPassword123!"
        password_data = {
            "current_password": "Password123!",
            "new_password": new_password
        }
        
        # Change password
        change_response = client.post("/api/v1/auth/change-password", 
                                    headers=auth_headers, 
                                    json=password_data)
        assert change_response.status_code == status.HTTP_200_OK
        
        # Test login with old password (should fail)
        old_login_data = {"email": test_user.email, "password": "Password123!"}
        old_login_response = client.post("/api/v1/login", json=old_login_data)
        assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test login with new password (should succeed)
        new_login_data = {"email": test_user.email, "password": new_password}
        new_login_response = client.post("/api/v1/login", json=new_login_data)
        assert new_login_response.status_code == status.HTTP_200_OK
        assert "access_token" in new_login_response.json()

    def test_change_password_multiple_times(self, client, test_user, db_session):
        """Test changing password multiple times in succession."""
        passwords = ["Password123!", "NewPassword1!", "AnotherPass2!", "FinalPassword3!"]
        
        # Start with login to get initial token
        login_data = {"email": test_user.email, "password": passwords[0]}
        login_response = client.post("/api/v1/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Change password multiple times
        for i in range(1, len(passwords)):
            password_data = {
                "current_password": passwords[i-1],
                "new_password": passwords[i]
            }
            
            response = client.post("/api/v1/auth/change-password", 
                                 headers=headers, 
                                 json=password_data)
            assert response.status_code == status.HTTP_200_OK
            
            # Verify new password works
            db_session.refresh(test_user)
            assert verify_password(passwords[i], test_user.hashed_password)

    def test_change_password_with_special_characters(self, client, auth_headers):
        """Test password change with various special characters."""
        special_passwords = [
            "Password123@",
            "Password123#",
            "Password123$",
            "Password123%",
            "Password123^",
            "Password123&",
            "Password123*",
            "Password123!?",
            "Password123<>",
            "Password123{}[]"
        ]
        
        for new_password in special_passwords:
            password_data = {
                "current_password": "Password123!",
                "new_password": new_password
            }
            
            response = client.post("/api/v1/auth/change-password", 
                                 headers=auth_headers, 
                                 json=password_data)
            
            # Should accept valid special characters
            assert response.status_code == status.HTTP_200_OK
            
            # Change back to original for next test
            reset_data = {
                "current_password": new_password,
                "new_password": "Password123!"
            }
            reset_response = client.post("/api/v1/auth/change-password", 
                                       headers=auth_headers, 
                                       json=reset_data)
            assert reset_response.status_code == status.HTTP_200_OK
