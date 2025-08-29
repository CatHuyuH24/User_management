"""
Comprehensive tests for user profile endpoints.
"""
import pytest
import json
import io
from fastapi import status


class TestUserProfileEndpoints:
    """Test cases for user profile management endpoints."""

    def test_get_user_profile(self, client, auth_headers, test_user):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_user_profile_unauthorized(self, client):
        """Test getting user profile without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_profile_valid_data(self, client, auth_headers, valid_profile_update):
        """Test updating user profile with valid data."""
        response = client.put("/api/v1/users/me", headers=auth_headers, json=valid_profile_update)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["first_name"] == valid_profile_update["first_name"]
        assert data["last_name"] == valid_profile_update["last_name"]
        assert data["year_of_birth"] == valid_profile_update["year_of_birth"]
        assert data["description"] == valid_profile_update["description"]

    def test_update_user_profile_partial_update(self, client, auth_headers):
        """Test partial profile update."""
        update_data = {"first_name": "NewFirstName"}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["first_name"] == "NewFirstName"

    def test_update_user_profile_invalid_data(self, client, auth_headers, invalid_profile_update):
        """Test updating user profile with invalid data."""
        response = client.put("/api/v1/users/me", headers=auth_headers, json=invalid_profile_update)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_user_profile_unauthorized(self, client, valid_profile_update):
        """Test updating profile without authentication."""
        response = client.put("/api/v1/users/me", json=valid_profile_update)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_avatar_valid_image(self, client, auth_headers):
        """Test uploading a valid avatar image."""
        # Create a simple test image
        image_content = b"fake_image_content"
        files = {
            "file": ("test_avatar.jpg", io.BytesIO(image_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "avatar_url" in data
        assert "user" in data
        assert data["message"] == "Avatar uploaded successfully"
        assert data["avatar_url"].startswith("/static/avatars/")

    def test_upload_avatar_invalid_file_type(self, client, auth_headers):
        """Test uploading invalid file type as avatar."""
        text_content = b"this is not an image"
        files = {
            "file": ("test.txt", io.BytesIO(text_content), "text/plain")
        }
        
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only image files" in response.json()["detail"]

    def test_upload_avatar_large_file(self, client, auth_headers):
        """Test uploading a file that's too large."""
        # Create a file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        files = {
            "file": ("large_image.jpg", io.BytesIO(large_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File size must be less than 5MB" in response.json()["detail"]

    def test_upload_avatar_unauthorized(self, client):
        """Test uploading avatar without authentication."""
        image_content = b"fake_image_content"
        files = {
            "file": ("test_avatar.jpg", io.BytesIO(image_content), "image/jpeg")
        }
        
        response = client.post("/api/v1/users/me/avatar", files=files)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_avatar_no_file(self, client, auth_headers):
        """Test uploading avatar without providing a file."""
        response = client.post("/api/v1/users/me/avatar", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_profile_empty_fields(self, client, auth_headers):
        """Test updating profile with empty fields."""
        update_data = {
            "first_name": "",
            "last_name": "",
            "description": ""
        }
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile_null_fields(self, client, auth_headers):
        """Test updating profile with null fields."""
        update_data = {
            "first_name": None,
            "last_name": None,
            "year_of_birth": None,
            "description": None
        }
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile_year_of_birth_validation(self, client, auth_headers):
        """Test year of birth validation."""
        test_cases = [
            (1899, False),  # Too old
            (1900, True),   # Minimum valid
            (2024, True),   # Maximum valid
            (2025, False),  # Future year
        ]
        
        for year, should_pass in test_cases:
            update_data = {"year_of_birth": year}
            response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
            
            if should_pass:
                assert response.status_code == status.HTTP_200_OK
                assert response.json()["year_of_birth"] == year
            else:
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_profile_description_length(self, client, auth_headers):
        """Test description length validation."""
        # Valid description
        valid_description = "A" * 1000
        update_data = {"description": valid_description}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == valid_description
        
        # Invalid description (too long)
        invalid_description = "A" * 1001
        update_data = {"description": invalid_description}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_profile_update_preserves_other_fields(self, client, auth_headers, test_user):
        """Test that partial update preserves other fields."""
        # Get initial profile
        response = client.get("/api/v1/users/me", headers=auth_headers)
        initial_profile = response.json()
        
        # Update only first name
        update_data = {"first_name": "NewFirstName"}
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        updated_profile = response.json()
        assert updated_profile["first_name"] == "NewFirstName"
        assert updated_profile["last_name"] == initial_profile["last_name"]
        assert updated_profile["email"] == initial_profile["email"]
        assert updated_profile["username"] == initial_profile["username"]

    def test_avatar_file_extension_handling(self, client, auth_headers):
        """Test that avatar upload handles different file extensions correctly."""
        test_cases = [
            ("test.jpg", "image/jpeg"),
            ("test.jpeg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.gif", "image/gif"),
        ]
        
        for filename, content_type in test_cases:
            image_content = b"fake_image_content"
            files = {
                "file": (filename, io.BytesIO(image_content), content_type)
            }
            
            response = client.post("/api/v1/users/me/avatar", headers=auth_headers, files=files)
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["avatar_url"].endswith(f".{filename.split('.')[-1]}")

    def test_avatar_url_update_via_profile(self, client, auth_headers):
        """Test updating avatar URL directly via profile update."""
        avatar_url = "/static/avatars/custom_avatar.jpg"
        update_data = {"avatar_url": avatar_url}
        
        response = client.put("/api/v1/users/me", headers=auth_headers, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["avatar_url"] == avatar_url
