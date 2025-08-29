"""
Test configuration and fixtures for the user service tests.
"""
import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
sys.path.insert(0, app_dir)

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from core.database import get_db, Base
from models.user import User, UserRole
from services.auth_service import auth_service

# Test database URL (using SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Import FastAPI's TestClient directly to avoid version conflicts
    from fastapi.testclient import TestClient as FastAPITestClient
    test_client = FastAPITestClient(app)
    
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    hashed_password = auth_service.get_password_hash("TestPassword123!")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        role=UserRole.CLIENT
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    hashed_password = auth_service.get_password_hash("AdminPassword123!")
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="Admin",
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def test_super_admin(db_session):
    """Create a test super admin user."""
    hashed_password = auth_service.get_password_hash("SuperAdminPassword123!")
    super_admin = User(
        username="testsuperadmin",
        email="superadmin@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="SuperAdmin",
        is_active=True,
        is_verified=True,
        role=UserRole.SUPER_ADMIN
    )
    db_session.add(super_admin)
    db_session.commit()
    db_session.refresh(super_admin)
    return super_admin

@pytest.fixture
def user_token(test_user):
    """Generate a valid JWT token for the test user."""
    return auth_service.create_full_access_token(test_user)

@pytest.fixture
def admin_token(test_admin):
    """Generate a valid JWT token for the test admin."""
    return auth_service.create_full_access_token(test_admin)

@pytest.fixture
def super_admin_token(test_super_admin):
    """Generate a valid JWT token for the test super admin."""
    return auth_service.create_full_access_token(test_super_admin)

@pytest.fixture
def auth_headers(user_token):
    """Authorization headers with user token."""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_auth_headers(admin_token):
    """Authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def super_admin_auth_headers(super_admin_token):
    """Authorization headers with super admin token."""
    return {"Authorization": f"Bearer {super_admin_token}"}

# Test data fixtures
@pytest.fixture
def valid_user_data():
    """Valid user registration data."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPassword123!",
        "first_name": "New",
        "last_name": "User"
    }

@pytest.fixture
def invalid_user_data():
    """Invalid user registration data for testing validation."""
    return {
        "username": "nu",  # Too short
        "email": "invalid-email",
        "password": "weak",  # Too weak
        "first_name": "A" * 101,  # Too long
        "last_name": "B" * 101   # Too long
    }

@pytest.fixture
def valid_login_data():
    """Valid login credentials."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

@pytest.fixture
def invalid_login_data():
    """Invalid login credentials."""
    return {
        "email": "test@example.com",
        "password": "WrongPassword123!"
    }

@pytest.fixture
def valid_profile_update():
    """Valid profile update data."""
    return {
        "first_name": "Updated",
        "last_name": "Name",
        "year_of_birth": 1990,
        "description": "Updated description"
    }

@pytest.fixture
def invalid_profile_update():
    """Invalid profile update data."""
    return {
        "year_of_birth": 1800,  # Too old
        "description": "A" * 1001  # Too long
    }
