import pytest
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from fastapi.testclient import TestClient
from main import app

def test_read_root():
    """Test root endpoint"""
    # Create client without context manager for newer httpx compatibility
    from fastapi.testclient import TestClient as FastAPITestClient
    client = FastAPITestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Enhanced User Management Service" in data["message"]

def test_health_check():
    """Test health check endpoint"""
    from fastapi.testclient import TestClient as FastAPITestClient
    client = FastAPITestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "enhanced-user-management"
