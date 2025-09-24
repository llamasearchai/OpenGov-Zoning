"""Tests for OpenGov Zoning core utilities."""

import pytest

from opengovzoning.core.config import Settings
from opengovzoning.core.database import SQLiteDatabaseManager


def test_settings():
    """Test settings configuration."""
    settings = Settings()
    assert settings.app_name == "OpenGov Zoning API"
    assert settings.app_version == "1.0.0"


def test_database_manager():
    """Test database manager."""
    db_manager = SQLiteDatabaseManager()
    db_manager.initialize(drop_existing=True)
    db_manager.seed_sample_data()

    items = db_manager.db["items"].rows
    assert len(list(items)) >= 2

