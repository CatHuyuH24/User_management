"""
Comprehensive tests for authentication endpoints.
"""
import pytest
import json
from fastapi import status


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_signup_valid_user(self, client, valid_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/signup", json=valid_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["message"] == "User created successfully. Please complete MFA setup on first login for enhanced security."
        assert "user" in data
        assert data["user"]["username"] == valid_user_data["username"]
        assert data["user"]["email"] == valid_user_data["email"]
        assert data["user"]["is_active"] is True
        assert "password" not in data["user"]  # Password should not be returned

    def test_signup_duplicate_email(self, client, test_user, valid_user_data):
        """Test registration with duplicate email."""
        valid_user_data["email"] = test_user.email
        response = client.post("/api/v1/signup", json=valid_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_signup_duplicate_username(self, client, test_user, valid_user_data):
        """Test registration with duplicate username."""
        valid_user_data["username"] = test_user.username
        response = client.post("/api/v1/signup", json=valid_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already taken" in response.json()["detail"]

    def test_signup_invalid_data(self, client, invalid_user_data):
        """Test registration with invalid data."""
        response = client.post("/api/v1/signup", json=invalid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_weak_password(self, client, valid_user_data):
        """Test registration with weak password."""
        valid_user_data["password"] = "weak"
        response = client.post("/api/v1/signup", json=valid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_valid_credentials_email(self, client, test_user, valid_login_data):
        """Test successful login with email."""
        response = client.post("/api/v1/login", json=valid_login_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data.get("mfa_required", False) is False

    def test_login_valid_credentials_username(self, client, test_user):
        """Test successful login with username."""
        login_data = {
            "username": test_user.username,
            "password": "TestPassword123!"
        }
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, invalid_login_data):
        """Test login with invalid credentials."""
        response = client.post("/api/v1/login", json=invalid_login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username/email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Password123!"
        }
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create inactive user
        inactive_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=get_password_hash("Password123!"),
            is_active=False,
            is_verified=True
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        login_data = {
            "email": "inactive@example.com",
            "password": "Password123!"
        }
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/api/v1/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_current_user_info(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "password" not in data

    def test_get_current_user_info_without_token(self, client):
        """Test getting current user info without authentication."""
        response = client.get("/api/v1/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_info_invalid_token(self, client):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/me", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_refresh_token(self, client, auth_headers):
        """Test token refresh."""
        response = client.post("/api/v1/refresh", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_token_without_auth(self, client):
        """Test token refresh without authentication."""
        response = client.post("/api/v1/refresh")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post("/api/v1/logout")
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.json()["message"]

    def test_signup_role_assignment(self, client, valid_user_data):
        """Test that new users get CLIENT role by default."""
        response = client.post("/api/v1/signup", json=valid_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["user"]["role"] == "client"

    def test_login_updates_last_login(self, client, test_user, valid_login_data, db_session):
        """Test that login updates the user's last_login timestamp."""
        # Get initial last_login
        initial_last_login = test_user.last_login
        
        # Login
        response = client.post("/api/v1/login", json=valid_login_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        db_session.refresh(test_user)
        
        # Check that last_login was updated
        assert test_user.last_login != initial_last_login
        assert test_user.last_login is not None

    def test_password_validation_requirements(self, client, valid_user_data):
        """Test password validation requirements."""
        test_cases = [
            ("short", "Password must be at least 8 characters"),
            ("nouppercase123!", "uppercase letter"),
            ("NOLOWERCASE123!", "lowercase letter"),
            ("NoDigits!", "digit"),
            ("NoSpecialChars123", "special character")
        ]
        
        for password, expected_error in test_cases:
            valid_user_data["password"] = password
            valid_user_data["email"] = f"test_{password}@example.com"
            valid_user_data["username"] = f"test_{password}"
            
            response = client.post("/api/v1/signup", json=valid_user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            # Note: Exact error message checking depends on validation implementation
