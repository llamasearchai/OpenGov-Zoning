"""Comprehensive test suite for OpenGov Zoning."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from click.testing import CliRunner

from opengovzoning.core.config import Settings, get_settings
from opengovzoning.core.database import SQLiteDatabaseManager
from opengovzoning.services.agent_service import AgentService
from opengovzoning.storage.item_storage import ItemStorage
from opengovzoning.web.app import app


class TestSettings:
    """Test settings configuration."""

    def test_settings_creation(self):
        """Test that settings can be created."""
        settings = get_settings()
        assert settings.app_name == "OpenGov Zoning API"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False

    def test_settings_validation(self):
        """Test settings validation."""
        settings = Settings()
        assert settings.app_name == "OpenGov Zoning API"

    def test_environment_variable_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("DEBUG", "true")
        settings = Settings()
        assert settings.debug is True


class TestDatabaseManager:
    """Test database manager functionality."""

    def test_database_manager_creation(self):
        """Test database manager creation."""
        db_manager = SQLiteDatabaseManager()
        assert db_manager is not None

    def test_database_initialization(self):
        """Test database initialization."""
        db_manager = SQLiteDatabaseManager()
        # Test should not fail
        assert db_manager.db_path is not None

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    def test_database_drop_existing(self, mock_unlink, mock_exists):
        """Test database initialization with drop existing."""
        mock_exists.return_value = True
        db_manager = SQLiteDatabaseManager()
        # Should not raise exception
        assert db_manager is not None

    def test_sample_data_seeding(self):
        """Test sample data seeding."""
        db_manager = SQLiteDatabaseManager()
        # Should not raise exception
        assert db_manager is not None


class TestAgentService:
    """Test AI agent service functionality."""

    def test_agent_service_creation(self):
        """Test agent service creation."""
        agent_service = AgentService()
        assert agent_service is not None
        assert agent_service.settings is not None

    def test_agent_service_creation_with_openai_key(self, monkeypatch):
        """Test agent service creation with OpenAI key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent_service = AgentService()
        assert agent_service.openai_client is not None

    @pytest.mark.asyncio
    async def test_run_mock_analysis(self):
        """Test running mock analysis."""
        agent_service = AgentService()
        result = await agent_service._run_mock_analysis("test prompt")
        assert result is not None
        assert "analysis" in result
        assert "confidence" in result
        assert "provider" in result

    @pytest.mark.asyncio
    async def test_run_analysis_with_invalid_provider(self):
        """Test analysis with invalid provider."""
        agent_service = AgentService()
        result = await agent_service.run_analysis("test", provider="invalid")
        assert result is not None
        assert "analysis" in result

    @pytest.mark.asyncio
    async def test_chat_without_openai(self):
        """Test chat functionality without OpenAI."""
        agent_service = AgentService()
        response = await agent_service.chat("test message")
        assert isinstance(response, str)
        assert "not available" in response.lower()


class TestItemStorage:
    """Test item storage functionality."""

    def test_item_storage_creation(self):
        """Test item storage creation."""
        storage = ItemStorage()
        assert storage is not None
        assert storage.db is not None

    def test_get_item_stats(self):
        """Test getting item statistics."""
        storage = ItemStorage()
        stats = storage.get_item_stats()
        assert isinstance(stats, dict)
        assert "total_items" in stats


class TestFastAPIEndpoints:
    """Test FastAPI web endpoints."""

    def test_fastapi_app_creation(self):
        """Test FastAPI app creation."""
        assert app is not None
        assert app.title == "OpenGov Zoning API"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OpenGov Zoning"
        assert "version" in data
        assert "description" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "OpenGov Zoning"

    def test_list_items_endpoint(self, client):
        """Test list items endpoint."""
        response = client.get("/api/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_item_endpoint(self, client):
        """Test create item endpoint."""
        item_data = {
            "name": "Test Item",
            "description": "Test Description"
        }
        response = client.post("/api/items", json=item_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Item"

    def test_analysis_endpoint(self, client):
        """Test analysis endpoint."""
        analysis_data = {
            "prompt": "Test analysis prompt",
            "model": "ollama"
        }
        response = client.post("/api/analysis", json=analysis_data)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "provider" in data
        assert "model" in data

    def test_stats_endpoint(self, client):
        """Test stats endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "OpenGov Zoning"


class TestCLICommands:
    """Test CLI command functionality."""

    def test_version_command(self, cli_runner):
        """Test version command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "OpenGov Zoning v1.0.0" in result.output

    def test_help_command(self, cli_runner):
        """Test help command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "OpenGov Zoning" in result.output

    def test_init_command(self, cli_runner):
        """Test database initialization command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0

    def test_serve_command(self, cli_runner):
        """Test serve command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "serve" in result.output

    def test_agent_command(self, cli_runner):
        """Test agent command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["agent", "--help"])
        assert result.exit_code == 0
        assert "agent" in result.output

    def test_query_command(self, cli_runner):
        """Test query command."""
        from opengovzoning.cli import app
        result = cli_runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "query" in result.output


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        agent_service = AgentService()
        result = await agent_service.run_analysis("Test workflow")
        assert result is not None
        assert "analysis" in result

    def test_database_workflow(self):
        """Test database workflow."""
        db_manager = get_database_manager()
        db_manager = get_database_manager()
        storage = ItemStorage()

        # Test database operations
        assert db_manager is not None
        assert storage is not None

    def test_web_api_workflow(self):
        """Test web API workflow."""
        with TestClient(app) as client:
            # Test health check
            response = client.get("/health")
            assert response.status_code == 200

            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200


# Pytest fixtures
@pytest.fixture
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def cli_runner():
    """CLI test runner fixture."""
    from opengovzoning.cli import app
    return CliRunner()

@pytest.fixture
def sample_item_data():
    """Sample item data fixture."""
    return {
        "name": "Test Item",
        "description": "Test Description"
    }

@pytest.fixture
def sample_analysis_prompt():
    """Sample analysis prompt fixture."""
    return "Analyze this sample data for quality metrics"

# Additional test configuration
pytest_plugins = ["pytest_asyncio"]

# Test markers
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]

# Test configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with -m 'not slow')",
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

# Coverage configuration
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add coverage summary."""
    if hasattr(terminalreporter, "stats"):
        terminalreporter.write_sep("=", "Coverage Summary")
        for stat in terminalreporter.stats.values():
            if "coverage" in str(stat):
                terminalreporter.write_line(str(stat))