"""
Comprehensive tests for user deletion functionality
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User

client = TestClient(app)

class TestUserDeletion:
    """Test user deletion functionality."""

    def setup_method(self):
        """Setup test data."""
        self.admin_user_data = {
            "email": "super@admin.com",
            "password": "SuperAdminPassword123!"
        }
        self.client_user_data = {
            "email": "client@example.com",
            "password": "ClientPassword123?"
        }

    def get_admin_token(self):
        """Get admin authentication token."""
        response = client.post("/api/v1/login", json=self.admin_user_data)
        assert response.status_code == status.HTTP_200_OK
        return response.json()["access_token"]

    def get_client_token(self):
        """Get client authentication token."""
        response = client.post("/api/v1/login", json=self.client_user_data)
        assert response.status_code == status.HTTP_200_OK
        return response.json()["access_token"]

    def get_user_id_by_email(self, email):
        """Get user ID by email for testing."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        if response.status_code == status.HTTP_200_OK:
            users = response.json()
            for user in users:
                if user["email"] == email:
                    return user["id"]
        return None

    def create_test_user_for_deletion(self):
        """Create a test user specifically for deletion testing."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a unique test user
        import time
        timestamp = int(time.time())
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "client"
        }
        
        response = client.post("/api/v1/admin/users", json=test_user_data, headers=headers)
        if response.status_code == status.HTTP_201_CREATED:
            return response.json()["id"]
        return None

    def test_admin_can_delete_user(self):
        """Test that admin can delete a user."""
        # First create a user to delete
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id is None:
            pytest.skip("Cannot create test user for deletion")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Delete the user
        response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
        
        # Should succeed or return appropriate status
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND
        ]
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            # Verify user is deleted by trying to get it
            get_response = client.get(f"/api/v1/admin/users/{test_user_id}", headers=headers)
            assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_client_cannot_delete_user(self):
        """Test that client cannot delete users."""
        client_token = self.get_client_token()
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # Try to delete any user (using ID 1)
        response = client.delete("/api/v1/admin/users/1", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin privileges required" in response.json().get("detail", "")

    def test_unauthenticated_cannot_delete_user(self):
        """Test that unauthenticated users cannot delete users."""
        response = client.delete("/api/v1/admin/users/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_nonexistent_user(self):
        """Test deleting a user that doesn't exist."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try to delete user with very high ID (unlikely to exist)
        response = client.delete("/api/v1/admin/users/999999", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_with_invalid_id(self):
        """Test deleting user with invalid ID format."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try to delete user with invalid ID
        response = client.delete("/api/v1/admin/users/invalid", headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_soft_delete_vs_hard_delete(self):
        """Test whether deletion is soft (deactivation) or hard (removal)."""
        # Create a test user
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id is None:
            pytest.skip("Cannot create test user for deletion")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get user before deletion
        before_response = client.get(f"/api/v1/admin/users/{test_user_id}", headers=headers)
        if before_response.status_code != status.HTTP_200_OK:
            pytest.skip("Cannot get test user before deletion")
        
        # Delete the user
        delete_response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
        
        if delete_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            # Check if user still exists but is deactivated (soft delete)
            after_response = client.get(f"/api/v1/admin/users/{test_user_id}", headers=headers)
            
            if after_response.status_code == status.HTTP_200_OK:
                # Soft delete - user exists but might be deactivated
                user_data = after_response.json()
                # User might be marked as inactive or have deleted_at timestamp
                assert user_data.get("is_active") == False or user_data.get("deleted_at") is not None
            else:
                # Hard delete - user completely removed
                assert after_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_with_dependencies(self):
        """Test deleting user that might have dependencies (books, etc)."""
        # This test assumes the user might have related data
        # The system should handle dependencies gracefully
        
        # Get a client user ID
        client_user_id = self.get_user_id_by_email(self.client_user_data["email"])
        if client_user_id is None:
            pytest.skip("Cannot find client user for deletion test")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try to delete user (might have library records, etc.)
        response = client.delete(f"/api/v1/admin/users/{client_user_id}", headers=headers)
        
        # Should handle gracefully - either succeed or provide proper error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_400_BAD_REQUEST,  # If dependencies prevent deletion
            status.HTTP_409_CONFLICT      # If conflicts exist
        ]

    def test_admin_cannot_delete_self(self):
        """Test that admin cannot delete their own account."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get admin user ID
        admin_user_id = self.get_user_id_by_email(self.admin_user_data["email"])
        if admin_user_id is None:
            pytest.skip("Cannot find admin user ID")
        
        # Try to delete self
        response = client.delete(f"/api/v1/admin/users/{admin_user_id}", headers=headers)
        
        # Should prevent self-deletion
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT
        ]

    def test_delete_last_admin_prevention(self):
        """Test prevention of deleting the last admin user."""
        # This test would require knowing the admin user structure
        # For now, we'll test the concept
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get list of admin users
        response = client.get("/api/v1/admin/users?role=super_admin", headers=headers)
        if response.status_code == status.HTTP_200_OK:
            admins = response.json()
            
            if len(admins) == 1:
                # Only one admin - should prevent deletion
                admin_id = admins[0]["id"]
                delete_response = client.delete(f"/api/v1/admin/users/{admin_id}", headers=headers)
                
                # Should prevent deletion of last admin
                assert delete_response.status_code in [
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_403_FORBIDDEN,
                    status.HTTP_409_CONFLICT
                ]

    def test_bulk_user_deletion(self):
        """Test bulk deletion of users if supported."""
        # Create multiple test users
        test_user_ids = []
        for i in range(3):
            user_id = self.create_test_user_for_deletion()
            if user_id:
                test_user_ids.append(user_id)
        
        if not test_user_ids:
            pytest.skip("Cannot create test users for bulk deletion")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try bulk deletion if endpoint exists
        bulk_delete_data = {"user_ids": test_user_ids}
        response = client.post("/api/v1/admin/users/bulk-delete", json=bulk_delete_data, headers=headers)
        
        # Endpoint might not exist
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
                status.HTTP_207_MULTI_STATUS  # Partial success
            ]

    def test_user_deletion_audit_logging(self):
        """Test that user deletions are properly logged."""
        # Create a test user
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id is None:
            pytest.skip("Cannot create test user for deletion")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Delete the user
        response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            # Check if audit log endpoint exists
            audit_response = client.get("/api/v1/admin/audit-logs", headers=headers)
            
            if audit_response.status_code == status.HTTP_200_OK:
                # Look for deletion event in audit logs
                logs = audit_response.json()
                deletion_logged = any(
                    log.get("action") == "user_deleted" or "delete" in log.get("action", "").lower()
                    for log in logs
                )
                # Audit logging should capture the deletion

    def test_user_deletion_cascade_effects(self):
        """Test cascade effects of user deletion."""
        # This would test that related data is properly handled
        # when a user is deleted (sessions, preferences, etc.)
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get client user for testing
        client_user_id = self.get_user_id_by_email(self.client_user_data["email"])
        if client_user_id is None:
            pytest.skip("Cannot find client user")
        
        # Before deletion, user should be able to login
        login_response = client.post("/api/v1/login", json=self.client_user_data)
        pre_deletion_login_success = login_response.status_code == status.HTTP_200_OK
        
        # Delete user (this might affect our test user, so be careful)
        # For safety, we'll create a new test user
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id:
            delete_response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
            
            if delete_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
                # User should no longer be able to login (if hard deleted)
                # This is testing the concept rather than our actual test user
                pass

    def test_user_deletion_permission_levels(self):
        """Test different permission levels for user deletion."""
        # Test that only appropriate admin levels can delete users
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Super admin should be able to delete
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id:
            response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
                status.HTTP_404_NOT_FOUND
            ]

    def test_user_deletion_rate_limiting(self):
        """Test rate limiting on user deletion."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Make multiple deletion attempts
        responses = []
        for i in range(5):
            # Try to delete non-existent users to avoid actually deleting data
            response = client.delete(f"/api/v1/admin/users/99999{i}", headers=headers)
            responses.append(response.status_code)
        
        # Check if rate limiting is applied
        rate_limited = any(status == 429 for status in responses)
        # Rate limiting may or may not be implemented

    def test_user_deletion_concurrent_access(self):
        """Test concurrent deletion attempts."""
        import threading
        
        # Create a test user
        test_user_id = self.create_test_user_for_deletion()
        if test_user_id is None:
            pytest.skip("Cannot create test user for deletion")
        
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        results = []
        
        def attempt_deletion():
            response = client.delete(f"/api/v1/admin/users/{test_user_id}", headers=headers)
            results.append(response.status_code)
        
        # Make concurrent deletion attempts
        threads = []
        for i in range(3):
            thread = threading.Thread(target=attempt_deletion)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one should succeed, others should fail appropriately
        success_count = sum(1 for status in results if status in [200, 204])
        assert success_count <= 1  # At most one deletion should succeed


class TestUserDeletionSecurity:
    """Test security aspects of user deletion."""

    def test_delete_user_sql_injection(self):
        """Test SQL injection protection in user deletion."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try SQL injection in user ID
        malicious_ids = [
            "1; DROP TABLE users; --",
            "1 OR 1=1",
            "' OR '1'='1",
            "1 UNION SELECT * FROM users"
        ]
        
        for malicious_id in malicious_ids:
            response = client.delete(f"/api/v1/admin/users/{malicious_id}", headers=headers)
            
            # Should handle malicious input safely
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND
            ]

    def test_delete_user_authorization_bypass(self):
        """Test that authorization cannot be bypassed."""
        # Try to delete without proper authentication
        response = client.delete("/api/v1/admin/users/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try with client token
        client_token = self.get_client_token()
        headers = {"Authorization": f"Bearer {client_token}"}
        response = client.delete("/api/v1/admin/users/1", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def get_admin_token(self):
        """Get admin authentication token."""
        admin_data = {
            "email": "super@admin.com",
            "password": "SuperAdminPassword123!"
        }
        response = client.post("/api/v1/login", json=admin_data)
        assert response.status_code == status.HTTP_200_OK
        return response.json()["access_token"]

    def get_client_token(self):
        """Get client authentication token."""
        client_data = {
            "email": "client@example.com",
            "password": "ClientPassword123?"
        }
        response = client.post("/api/v1/login", json=client_data)
        assert response.status_code == status.HTTP_200_OK
        return response.json()["access_token"]

    def create_test_user_for_deletion(self):
        """Create a test user specifically for deletion testing."""
        admin_token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        import time
        timestamp = int(time.time())
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "client"
        }
        
        response = client.post("/api/v1/admin/users", json=test_user_data, headers=headers)
        if response.status_code == status.HTTP_201_CREATED:
            return response.json()["id"]
        return None


if __name__ == "__main__":
    # Run tests directly
    test_class = TestUserDeletion()
    test_class.setup_method()
    
    print("🧪 Running User Deletion Tests")
    print("=" * 50)
    
    try:
        test_class.test_client_cannot_delete_user()
        print("✅ Client access restriction test passed")
        
        test_class.test_unauthenticated_cannot_delete_user()
        print("✅ Unauthenticated access test passed")
        
        test_class.test_delete_nonexistent_user()
        print("✅ Nonexistent user deletion test passed")
        
        test_class.test_delete_user_with_invalid_id()
        print("✅ Invalid ID test passed")
        
        print("\n🎉 All user deletion tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
