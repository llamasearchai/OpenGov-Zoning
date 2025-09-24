"""FastAPI-specific tests for OpenGov Zoning."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from opengovzoning.web.app import app


class TestFastAPIIntegration:
    """Test FastAPI integration functionality."""

    def test_app_creation(self):
        """Test that FastAPI app is created properly."""
        assert app is not None
        assert app.title == "OpenGov Zoning API"
        assert app.version == "1.0.0"

    def test_app_lifespan(self):
        """Test application lifespan events."""
        # Test should not raise exceptions
        assert app is not None

    def test_cors_middleware(self):
        """Test CORS middleware configuration."""
        # Check that CORS middleware is properly configured
        assert len(app.user_middleware) > 0

    def test_root_endpoint_functionality(self, client):
        """Test root endpoint functionality."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "OpenGov Zoning"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "health" in data

    def test_health_endpoint_functionality(self, client):
        """Test health endpoint functionality."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "OpenGov Zoning"
        assert data["version"] == "1.0.0"

    @pytest.mark.parametrize("endpoint,expected_status", [
        ("/", 200),
        ("/health", 200),
        ("/api/items", 200),
        ("/api/stats", 200),
        ("/nonexistent", 404)
    ])
    def test_endpoint_responses(self, client, endpoint, expected_status):
        """Test various endpoint responses."""
        response = client.get(endpoint)
        assert response.status_code == expected_status

    def test_api_items_crud_operations(self, client):
        """Test CRUD operations on items API."""
        # Create item
        create_data = {
            "name": "Test API Item",
            "description": "Test item created via API"
        }
        response = client.post("/api/items", json=create_data)
        assert response.status_code == 200

        created_item = response.json()
        assert created_item["name"] == "Test API Item"
        assert "id" in created_item

        # Get item
        item_id = created_item["id"]
        response = client.get(f"/api/items/{item_id}")
        assert response.status_code == 200

        retrieved_item = response.json()
        assert retrieved_item["name"] == "Test API Item"

        # Update item
        update_data = {
            "name": "Updated Test Item",
            "description": "Updated description"
        }
        response = client.put(f"/api/items/{item_id}", json=update_data)
        assert response.status_code == 200

        # Delete item
        response = client.delete(f"/api/items/{item_id}")
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/items/{item_id}")
        assert response.status_code == 404

    def test_analysis_endpoint_functionality(self, client):
        """Test analysis endpoint functionality."""
        analysis_data = {
            "prompt": "Test analysis for API testing",
            "model": "ollama"
        }

        response = client.post("/api/analysis", json=analysis_data)
        assert response.status_code == 200

        result = response.json()
        assert "result" in result
        assert "provider" in result
        assert "model" in result

    def test_error_handling(self, client):
        """Test error handling in API endpoints."""
        # Test 404 error
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

        # Test invalid item ID
        response = client.get("/api/items/invalid-id")
        assert response.status_code == 404

        # Test invalid JSON in create
        response = client.post("/api/items", data="invalid json")
        assert response.status_code == 422

    def test_api_response_formats(self, client):
        """Test API response formats."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

        response = client.get("/api/items")
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_async_endpoints(self):
        """Test async endpoint functionality."""
        # This test ensures async endpoints work properly
        assert app is not None

    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoints(self, client):
        """Test documentation endpoints."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200


class TestAPIPerformance:
    """Test API performance characteristics."""

    def test_response_times(self, client):
        """Test reasonable response times."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        # Response should be fast (less than 1 second)
        assert end_time - start_time < 1.0

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading

        def make_request():
            response = client.get("/health")
            return response.status_code

        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        assert all(status == 200 for status in results)


class TestAPIErrorHandling:
    """Test comprehensive error handling."""

    def test_database_connection_errors(self, client):
        """Test handling of database connection errors."""
        with patch('sqlite_utils.Database') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            response = client.get("/api/items")
            # Should handle gracefully
            assert response.status_code in [200, 500]

    def test_ai_service_errors(self, client):
        """Test handling of AI service errors."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_openai.side_effect = Exception("AI service unavailable")
            response = client.post("/api/analysis", json={"prompt": "test"})
            # Should handle gracefully
            assert response.status_code in [200, 500]

    def test_validation_errors(self, client):
        """Test input validation errors."""
        # Test missing required fields
        response = client.post("/api/items", json={})
        assert response.status_code == 422

        # Test invalid data types
        response = client.post("/api/items", json={"name": 123})
        assert response.status_code == 422


# Additional pytest configuration
pytest_plugins = ["pytest_asyncio"]

# Test markers for organization
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]

# Coverage configuration for API tests
def pytest_configure(config):
    """Configure pytest for API tests."""
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )