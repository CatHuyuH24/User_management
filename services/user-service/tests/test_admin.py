"""
Comprehensive tests for admin endpoints.
"""
import pytest
import json
from fastapi import status


class TestAdminEndpoints:
    """Test cases for admin management endpoints."""

    def test_admin_dashboard_stats(self, client, admin_auth_headers):
        """Test getting admin dashboard statistics."""
        response = client.get("/api/v1/admin/dashboard", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "verified_users" in data
        assert "users_with_mfa" in data
        assert "new_users_today" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["active_users"], int)

    def test_admin_dashboard_unauthorized(self, client, auth_headers):
        """Test accessing admin dashboard as regular user."""
        response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_dashboard_no_auth(self, client):
        """Test accessing admin dashboard without authentication."""
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_all_users(self, client, admin_auth_headers, test_user):
        """Test getting all users as admin."""
        response = client.get("/api/v1/admin/users", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test user
        
        # Check if test user is in the list
        user_ids = [user["id"] for user in data]
        assert test_user.id in user_ids

    def test_get_all_users_with_pagination(self, client, admin_auth_headers):
        """Test getting users with pagination."""
        response = client.get("/api/v1/admin/users?skip=0&limit=1", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1

    def test_get_all_users_with_search(self, client, admin_auth_headers, test_user):
        """Test getting users with search filter."""
        response = client.get(f"/api/v1/admin/users?search={test_user.username}", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        # Should find the test user
        assert any(user["username"] == test_user.username for user in data)

    def test_get_all_users_with_filters(self, client, admin_auth_headers):
        """Test getting users with various filters."""
        # Test role filter
        response = client.get("/api/v1/admin/users?role=client", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Test active filter
        response = client.get("/api/v1/admin/users?is_active=true", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Test verified filter
        response = client.get("/api/v1/admin/users?is_verified=true", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_delete_user_soft_delete(self, client, admin_auth_headers, db_session):
        """Test soft deleting a user."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create a user to delete
        user_to_delete = User(
            username="deleteme",
            email="deleteme@example.com",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user_to_delete)
        db_session.commit()
        db_session.refresh(user_to_delete)
        
        # Soft delete the user
        deletion_data = {
            "reason": "Test deletion",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            f"/api/v1/admin/users/{user_to_delete.id}",
            headers=admin_auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "User deleted successfully"
        assert data["user_id"] == user_to_delete.id
        assert data["permanent"] is False
        assert "recoverable_until" in data
        
        # Verify user is marked as inactive
        db_session.refresh(user_to_delete)
        assert user_to_delete.is_active is False
        assert user_to_delete.deleted_at is not None

    def test_delete_user_permanent(self, client, admin_auth_headers, db_session):
        """Test permanently deleting a user."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create a user to delete
        user_to_delete = User(
            username="deleteme2",
            email="deleteme2@example.com",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user_to_delete)
        db_session.commit()
        user_id = user_to_delete.id
        
        # Permanently delete the user
        deletion_data = {
            "reason": "Test permanent deletion",
            "permanent": True,
            "notify_user": False
        }
        
        response = client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=admin_auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["permanent"] is True
        assert data["recoverable_until"] is None
        
        # Verify user is actually deleted from database
        deleted_user = db_session.query(User).filter(User.id == user_id).first()
        assert deleted_user is None

    def test_delete_nonexistent_user(self, client, admin_auth_headers):
        """Test deleting a non-existent user."""
        deletion_data = {
            "reason": "Test deletion",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            "/api/v1/admin/users/99999",
            headers=admin_auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

    def test_delete_self_prevention(self, client, admin_auth_headers, test_admin):
        """Test that admin cannot delete their own account."""
        deletion_data = {
            "reason": "Self deletion attempt",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            f"/api/v1/admin/users/{test_admin.id}",
            headers=admin_auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete your own account" in response.json()["detail"]

    def test_delete_super_admin_by_admin(self, client, admin_auth_headers, test_super_admin):
        """Test that regular admin cannot delete super admin."""
        deletion_data = {
            "reason": "Attempt to delete super admin",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            f"/api/v1/admin/users/{test_super_admin.id}",
            headers=admin_auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot delete super admin" in response.json()["detail"]

    def test_delete_user_unauthorized(self, client, auth_headers):
        """Test deleting user as regular user (should fail)."""
        deletion_data = {
            "reason": "Test deletion",
            "permanent": False,
            "notify_user": False
        }
        
        response = client.delete(
            "/api/v1/admin/users/1",
            headers=auth_headers,
            json=deletion_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_admin_user(self, client, super_admin_auth_headers):
        """Test creating a new user as admin."""
        user_data = {
            "username": "newadminuser",
            "email": "newadmin@example.com",
            "password": "AdminPassword123!",
            "first_name": "New",
            "last_name": "Admin",
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "send_welcome_email": False
        }
        
        response = client.post("/api/v1/admin/users", headers=super_admin_auth_headers, json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
        assert "password" not in data

    def test_update_user_by_admin(self, client, admin_auth_headers, test_user):
        """Test updating a user as admin."""
        update_data = {
            "first_name": "UpdatedByAdmin",
            "is_verified": True
        }
        
        response = client.put(
            f"/api/v1/admin/users/{test_user.id}",
            headers=admin_auth_headers,
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["first_name"] == "UpdatedByAdmin"
        assert data["is_verified"] is True

    def test_reset_user_password(self, client, admin_auth_headers, test_user):
        """Test resetting user password as admin."""
        reset_data = {
            "new_password": "NewPassword123!",
            "require_change": True,
            "notify_user": False
        }
        
        response = client.post(
            f"/api/v1/admin/users/{test_user.id}/reset-password",
            headers=admin_auth_headers,
            json=reset_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "Password reset successfully" in data["message"]

    def test_admin_actions_require_authentication(self, client):
        """Test that all admin actions require authentication."""
        endpoints = [
            ("GET", "/api/v1/admin/dashboard"),
            ("GET", "/api/v1/admin/users"),
            ("DELETE", "/api/v1/admin/users/1"),
            ("POST", "/api/v1/admin/users"),
            ("PUT", "/api/v1/admin/users/1"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "DELETE":
                response = client.delete(endpoint, json={"reason": "test", "permanent": False, "notify_user": False})
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_regular_user_cannot_access_admin_endpoints(self, client, auth_headers):
        """Test that regular users cannot access admin endpoints."""
        endpoints = [
            ("GET", "/api/v1/admin/dashboard"),
            ("GET", "/api/v1/admin/users"),
            ("DELETE", "/api/v1/admin/users/1"),
            ("POST", "/api/v1/admin/users"),
            ("PUT", "/api/v1/admin/users/1"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=auth_headers, json={"reason": "test", "permanent": False, "notify_user": False})
            elif method == "POST":
                response = client.post(endpoint, headers=auth_headers, json={})
            elif method == "PUT":
                response = client.put(endpoint, headers=auth_headers, json={})
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
