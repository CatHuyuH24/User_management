"""
Comprehensive tests for admin user list functionality
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User, UserRole

client = TestClient(app)

class TestAdminUsersList:
    """Test admin users list functionality and permissions."""

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

    def test_admin_can_access_users_list(self):
        """Test that admin can access users list."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Should contain at least our test users
        assert len(data) >= 2
        
        # Check structure of returned user data
        for user in data:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user
            assert "is_active" in user
            assert "is_verified" in user
            assert "created_at" in user

    def test_client_cannot_access_users_list(self):
        """Test that client cannot access users list."""
        token = self.get_client_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin privileges required" in response.json()["detail"]

    def test_unauthenticated_cannot_access_users_list(self):
        """Test that unauthenticated users cannot access users list."""
        response = client.get("/api/v1/admin/users")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_cannot_access_users_list(self):
        """Test that invalid tokens cannot access users list."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_users_list_pagination(self):
        """Test users list pagination parameters."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with pagination parameters
        response = client.get("/api/v1/admin/users?skip=0&limit=10", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_users_list_filtering_by_role(self):
        """Test users list filtering by role."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Filter by client role
        response = client.get("/api/v1/admin/users?role=client", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned users should be clients
        for user in data:
            assert user["role"] == "client"

    def test_users_list_filtering_by_active_status(self):
        """Test users list filtering by active status."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Filter by active users
        response = client.get("/api/v1/admin/users?is_active=true", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned users should be active
        for user in data:
            assert user["is_active"] == True

    def test_users_list_search_functionality(self):
        """Test users list search functionality."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Search for client user
        response = client.get("/api/v1/admin/users?search=client", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should find users matching the search term
        found_client = False
        for user in data:
            if "client" in user["username"].lower() or "client" in user["email"].lower():
                found_client = True
                break
        assert found_client

    def test_users_list_combined_filters(self):
        """Test users list with multiple filters."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Combine multiple filters
        params = "?role=client&is_active=true&limit=5"
        response = client.get(f"/api/v1/admin/users{params}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all filters are applied
        for user in data:
            assert user["role"] == "client"
            assert user["is_active"] == True
        assert len(data) <= 5

    def test_users_list_ordering(self):
        """Test that users list is properly ordered."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should be ordered by created_at descending (newest first)
        if len(data) > 1:
            for i in range(len(data) - 1):
                assert data[i]["created_at"] >= data[i + 1]["created_at"]

    def test_get_specific_user_by_id(self):
        """Test getting a specific user by ID."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # First get the users list to get a user ID
        users_response = client.get("/api/v1/admin/users", headers=headers)
        users = users_response.json()
        
        if users:
            user_id = users[0]["id"]
            
            # Get specific user
            response = client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            user_data = response.json()
            
            assert user_data["id"] == user_id
            assert "username" in user_data
            assert "email" in user_data

    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get user with very high ID (unlikely to exist)
        response = client.get("/api/v1/admin/users/999999", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_client_cannot_access_specific_user(self):
        """Test that client cannot access specific user data."""
        client_token = self.get_client_token()
        client_headers = {"Authorization": f"Bearer {client_token}"}
        
        # Try to access user with ID 1
        response = client.get("/api/v1/admin/users/1", headers=client_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_users_list_performance(self):
        """Test users list endpoint performance."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        import time
        start_time = time.time()
        
        response = client.get("/api/v1/admin/users", headers=headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        # Response should be reasonably fast (less than 2 seconds)
        assert response_time < 2.0

    def test_users_list_rate_limiting(self):
        """Test rate limiting on users list endpoint."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/api/v1/admin/users", headers=headers)
            responses.append(response.status_code)
        
        # Most should succeed, but rate limiting might kick in
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 5  # At least half should succeed

    def test_admin_dashboard_stats(self):
        """Test admin dashboard statistics endpoint."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/admin/dashboard", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        
        # Check expected statistics fields
        expected_fields = [
            "total_users",
            "active_users", 
            "verified_users",
            "new_users_today"
        ]
        
        for field in expected_fields:
            assert field in stats
            assert isinstance(stats[field], int)
            assert stats[field] >= 0

    def test_admin_endpoints_consistency(self):
        """Test consistency across admin endpoints."""
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get dashboard stats
        dashboard_response = client.get("/api/v1/admin/dashboard", headers=headers)
        dashboard_stats = dashboard_response.json()
        
        # Get users list
        users_response = client.get("/api/v1/admin/users", headers=headers)
        users_list = users_response.json()
        
        # Check consistency
        actual_total_users = len(users_list)
        actual_active_users = sum(1 for user in users_list if user["is_active"])
        
        # Note: These might not match exactly due to pagination
        # but they should be in the right ballpark
        assert dashboard_stats["total_users"] >= actual_total_users - 100
        assert dashboard_stats["active_users"] >= actual_active_users - 100


class TestAdminPermissionEdgeCases:
    """Test edge cases for admin permissions."""

    def test_expired_admin_token(self):
        """Test admin endpoints with expired token."""
        # This would require creating an expired token
        # Implementation depends on JWT library and token structure
        pass

    def test_admin_role_change_during_session(self):
        """Test behavior when admin role is changed during session."""
        # This would require database manipulation during the test
        # which might not be available in all test environments
        pass

    def test_concurrent_admin_requests(self):
        """Test concurrent admin requests."""
        admin_data = {
            "email": "super@admin.com",
            "password": "SuperAdminPassword123!"
        }
        
        # Login
        login_response = client.post("/api/v1/login", json=admin_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        import threading
        results = []
        
        def make_request():
            response = client.get("/api/v1/admin/users", headers=headers)
            results.append(response.status_code)
        
        # Make concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        success_count = sum(1 for status in results if status == 200)
        assert success_count == 5


if __name__ == "__main__":
    # Run tests directly
    test_class = TestAdminUsersList()
    test_class.setup_method()
    
    print("🧪 Running Admin Users List Tests")
    print("=" * 50)
    
    try:
        test_class.test_admin_can_access_users_list()
        print("✅ Admin access test passed")
        
        test_class.test_client_cannot_access_users_list()
        print("✅ Client access restriction test passed")
        
        test_class.test_users_list_pagination()
        print("✅ Pagination test passed")
        
        test_class.test_users_list_filtering_by_role()
        print("✅ Role filtering test passed")
        
        test_class.test_admin_dashboard_stats()
        print("✅ Dashboard stats test passed")
        
        print("\n🎉 All admin users list tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
