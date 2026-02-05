"""
Unit tests for main application
"""

import pytest
from fastapi.testclient import TestClient


def test_import_app():
    """Test that app can be imported"""
    from app.main import app
    assert app is not None


def test_root_endpoint():
    """Test root endpoint"""
    from app.main import app
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    """Test health check endpoint"""
    from app.main import app
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
