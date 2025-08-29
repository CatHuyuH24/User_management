"""
Integration tests for the complete user service functionality.
"""
import pytest
import json
import io
from fastapi import status


class TestUserServiceIntegration:
    """End-to-end integration tests for user service."""

    def test_complete_user_lifecycle(self, client, db_session):
        """Test complete user lifecycle: signup -> login -> profile update -> avatar upload."""
        
        # 1. Sign up a new user
        signup_data = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "IntegrationPassword123!",
            "first_name": "Integration",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/signup", json=signup_data)
        assert response.status_code == status.HTTP_201_CREATED
        user_data = response.json()["user"]
        
        # 2. Login with the new user
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Get user profile
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        profile = response.json()
        assert profile["username"] == signup_data["username"]
        assert profile["email"] == signup_data["email"]
        
        # 4. Update profile
        update_data = {
            "first_name": "UpdatedIntegration",
            "year_of_birth": 1990,
            "description": "Integration test user"
        }
        
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated_profile = response.json()
        assert updated_profile["first_name"] == "UpdatedIntegration"
        assert updated_profile["year_of_birth"] == 1990
        
        # 5. Upload avatar
        image_content = b"fake_image_content"
        files = {
            "file": ("avatar.jpg", io.BytesIO(image_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
        assert response.status_code == status.HTTP_200_OK
        avatar_response = response.json()
        assert "avatar_url" in avatar_response
        assert avatar_response["avatar_url"].startswith("/static/avatars/")

    def test_admin_user_management_workflow(self, client, db_session):
        """Test admin workflow: create admin -> login -> manage users."""
        
        # 1. Create super admin user directly in database
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        
        super_admin = User(
            username="testworkflowadmin",
            email="workflowadmin@example.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_active=True,
            is_verified=True,
            role=UserRole.SUPER_ADMIN
        )
        db_session.add(super_admin)
        db_session.commit()
        db_session.refresh(super_admin)
        
        # 2. Login as admin
        login_data = {
            "email": "workflowadmin@example.com",
            "password": "AdminPassword123!"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create a regular user
        regular_user = User(
            username="regularworkflowuser",
            email="regularuser@example.com",
            hashed_password=get_password_hash("UserPassword123!"),
            is_active=True,
            is_verified=True,
            role=UserRole.CLIENT
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        
        # 4. Get dashboard stats
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert stats["total_users"] >= 2  # At least admin and regular user
        
        # 5. Get all users
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) >= 2
        
        # 6. Update the regular user
        update_data = {
            "first_name": "UpdatedByAdmin",
            "is_verified": True
        }
        
        response = client.put(
            f"/api/v1/admin/users/{regular_user.id}",
            headers=admin_headers,
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 7. Soft delete the regular user
        deletion_data = {
            "reason": "Integration test deletion",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            f"/api/v1/admin/users/{regular_user.id}",
            headers=admin_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deactivated
        db_session.refresh(regular_user)
        assert regular_user.is_active is False
        assert regular_user.deleted_at is not None

    def test_authentication_security(self, client, test_user):
        """Test various authentication security scenarios."""
        
        # 1. Test login with valid credentials
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        valid_token = response.json()["access_token"]
        
        # 2. Test access with valid token
        auth_headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Test access with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=invalid_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # 4. Test access without token
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # 5. Test token refresh
        response = client.post("/api/v1/refresh", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        new_token = response.json()["access_token"]
        assert new_token != valid_token

    def test_role_based_access_control(self, client, db_session):
        """Test role-based access control across different user roles."""
        
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        
        # Create users with different roles
        client_user = User(
            username="rbacclient",
            email="client@example.com",
            hashed_password=get_password_hash("ClientPassword123!"),
            is_active=True,
            is_verified=True,
            role=UserRole.CLIENT
        )
        
        admin_user = User(
            username="rbacadmin",
            email="admin@example.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_active=True,
            is_verified=True,
            role=UserRole.ADMIN
        )
        
        super_admin_user = User(
            username="rbacsuperadmin",
            email="superadmin@example.com",
            hashed_password=get_password_hash("SuperAdminPassword123!"),
            is_active=True,
            is_verified=True,
            role=UserRole.SUPER_ADMIN
        )
        
        db_session.add_all([client_user, admin_user, super_admin_user])
        db_session.commit()
        
        # Get tokens for each user type
        tokens = {}
        for user, password in [
            (client_user, "ClientPassword123!"),
            (admin_user, "AdminPassword123!"),
            (super_admin_user, "SuperAdminPassword123!")
        ]:
            login_data = {"email": user.email, "password": password}
            response = client.post("/api/v1/login", json=login_data)
            assert response.status_code == status.HTTP_200_OK
            tokens[user.role] = response.json()["access_token"]
        
        # Test client access
        client_headers = {"Authorization": f"Bearer {tokens[UserRole.CLIENT]}"}
        
        # Client can access their own profile
        response = client.get("/api/v1/users/me", headers=client_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Client cannot access admin endpoints
        response = client.get("/api/v1/admin/dashboard", headers=client_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test admin access
        admin_headers = {"Authorization": f"Bearer {tokens[UserRole.ADMIN]}"}
        
        # Admin can access admin dashboard
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Admin can manage users
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_data_validation_edge_cases(self, client):
        """Test edge cases for data validation."""
        
        # Test username validation
        test_cases = [
            {"username": "ab", "email": "test@example.com", "password": "Password123!"},  # Too short
            {"username": "valid_user_123", "email": "invalid-email", "password": "Password123!"},  # Invalid email
            {"username": "valid_user", "email": "test@example.com", "password": "weak"},  # Weak password
            {"username": "user with spaces", "email": "test@example.com", "password": "Password123!"},  # Invalid username
        ]
        
        for invalid_data in test_cases:
            response = client.post("/api/v1/signup", json=invalid_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_concurrent_user_operations(self, client, db_session):
        """Test handling of concurrent user operations."""
        
        # Create multiple users with similar data to test uniqueness constraints
        base_data = {
            "username": "concurrentuser",
            "email": "concurrent@example.com",
            "password": "ConcurrentPassword123!",
            "first_name": "Concurrent",
            "last_name": "User"
        }
        
        # First user should succeed
        response1 = client.post("/api/v1/signup", json=base_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second user with same email should fail
        base_data["username"] = "concurrentuser2"
        response2 = client.post("/api/v1/signup", json=base_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response2.json()["detail"]
        
        # Third user with same username should fail
        base_data["email"] = "concurrent2@example.com"
        base_data["username"] = "concurrentuser"  # Back to original username
        response3 = client.post("/api/v1/signup", json=base_data)
        assert response3.status_code == status.HTTP_400_BAD_REQUEST
        assert "already taken" in response3.json()["detail"]

    def test_error_handling_and_recovery(self, client, test_user):
        """Test error handling and recovery scenarios."""
        
        # Login to get valid token
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid file upload
        text_content = b"this is not an image"
        files = {
            "file": ("test.txt", io.BytesIO(text_content), "text/plain")
        }
        
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # After error, normal operations should still work
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Test profile update with invalid data
        invalid_update = {"year_of_birth": 1800}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=invalid_update)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Valid update should still work after error
        valid_update = {"first_name": "RecoveredUser"}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=valid_update)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "RecoveredUser"
