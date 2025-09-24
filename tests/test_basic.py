"""Basic functionality tests for OpenGov Zoning."""

import pytest
from fastapi.testclient import TestClient

from opengovzoning.web.app import app


class TestBasicFunctionality:
    """Test basic application functionality."""

    def test_fastapi_app_creation(self):
        """Test FastAPI app creation."""
        assert app is not None
        assert app.title == "OpenGov Zoning API"

    def test_root_endpoint(self):
        """Test root endpoint."""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "OpenGov Zoning"
            assert "version" in data
            assert "description" in data

    def test_health_endpoint(self):
        """Test health check endpoint."""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "OpenGov Zoning"

    def test_stats_endpoint(self):
        """Test stats endpoint."""
        with TestClient(app) as client:
            response = client.get("/api/stats")
            assert response.status_code == 200
            data = response.json()
            assert "service" in data
            assert data["service"] == "OpenGov Zoning"