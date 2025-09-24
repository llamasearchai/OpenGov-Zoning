"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from opengovzoning.web.app import app


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db_manager():
    """Mock database manager fixture."""
    mock_db = Mock()
    mock_db.get_async_session.return_value.__aenter__.return_value = Mock()
    return mock_db


@pytest.fixture
def mock_agent_service():
    """Mock agent service fixture."""
    mock_service = Mock()
    mock_service.process_request.return_value = {
        "status": "success",
        "message": "Request processed successfully"
    }
    return mock_service
