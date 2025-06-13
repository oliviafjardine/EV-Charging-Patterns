"""
Test main application functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "EV Charging Analytics Platform API" in data["message"]


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_openapi_docs():
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_v1_prefix():
    """Test that API v1 endpoints are properly prefixed."""
    # This will fail initially since we need the database running
    # but it tests the route structure
    response = client.get("/api/v1/analytics/overview")
    # We expect either 200 (success) or 500 (database not available)
    # but not 404 (route not found)
    assert response.status_code != 404
