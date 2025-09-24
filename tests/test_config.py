"""Comprehensive tests for configuration management."""

import os
import pytest
from unittest.mock import patch

from opengovzoning.core.config import Settings, get_settings, reset_settings


class TestSettings:
    """Test Settings class functionality."""

    def test_settings_initialization(self):
        """Test that settings can be initialized with default values."""
        settings = Settings()
        assert settings.app_name == "OpenGov Zoning API"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.api_v1_prefix == "/api/v1"

    def test_settings_environment_variables(self):
        """Test that settings can be overridden by environment variables."""
        with patch.dict(os.environ, {
            "APP_ENV": "production",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test",
            "OPENAI_API_KEY": "test-key"
        }):
            settings = Settings()
            assert settings.app_env == "production"
            assert settings.debug is True
            assert settings.database_url == "postgresql://test"
            assert settings.openai_api_key == "test-key"

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string and list."""
        # Test string parsing
        with patch.dict(os.environ, {"CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"}):
            settings = Settings()
            assert settings.cors_origins == ["http://localhost:3000", "http://localhost:8080"]

        # Test list parsing
        with patch.dict(os.environ, {"CORS_ORIGINS": "['https://app.com', 'https://admin.com']"}):
            settings = Settings()
            assert settings.cors_origins == ["https://app.com", "https://admin.com"]

    def test_cors_methods_parsing(self):
        """Test CORS methods parsing."""
        with patch.dict(os.environ, {"CORS_ALLOW_METHODS": "GET,POST,PUT"}):
            settings = Settings()
            assert settings.cors_allow_methods == ["GET", "POST", "PUT"]

    def test_invalid_cors_origins(self):
        """Test that invalid CORS origins raise ValueError."""
        with patch.dict(os.environ, {"CORS_ORIGINS": "invalid-format"}):
            with pytest.raises(ValueError):
                Settings()

    def test_environment_properties(self):
        """Test environment detection properties."""
        # Test development environment
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            settings = Settings()
            assert settings.is_development is True
            assert settings.is_production is False
            assert settings.is_testing is False

        # Test production environment
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is True
            assert settings.is_testing is False

        # Test testing environment
        with patch.dict(os.environ, {"APP_ENV": "test"}):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is False
            assert settings.is_testing is True

    def test_database_pool_settings(self):
        """Test database connection pool settings."""
        settings = Settings()
        assert settings.db_pool_size == 20
        assert settings.db_max_overflow == 30
        assert settings.db_pool_timeout == 30
        assert settings.db_pool_recycle == 3600

    def test_redis_configuration(self):
        """Test Redis configuration settings."""
        settings = Settings()
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.redis_cache_ttl == 3600

    def test_jwt_configuration(self):
        """Test JWT configuration settings."""
        settings = Settings()
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_access_token_expire_minutes == 30
        assert settings.jwt_refresh_token_expire_days == 7

    def test_file_upload_configuration(self):
        """Test file upload configuration."""
        settings = Settings()
        assert settings.max_upload_size_mb == 50
        assert settings.upload_dir == "./uploads"
        assert "pdf" in settings.supported_formats
        assert "docx" in settings.supported_formats

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        settings = Settings()
        assert settings.rate_limit_requests == 100
        assert settings.rate_limit_window == 60

    def test_logging_configuration(self):
        """Test logging configuration."""
        settings = Settings()
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.log_file == "./logs/opengov_zoning.log"

    def test_feature_flags(self):
        """Test feature flag configuration."""
        settings = Settings()
        assert settings.enable_registration is True
        assert settings.enable_file_upload is True
        assert settings.enable_gis_integration is True
        assert settings.enable_email_notifications is True

    def test_performance_settings(self):
        """Test performance-related settings."""
        settings = Settings()
        assert settings.max_concurrent_analyses == 5
        assert settings.confidence_threshold == 0.85
        assert settings.max_document_size_mb == 50

    def test_cache_settings(self):
        """Test cache configuration."""
        settings = Settings()
        assert settings.cache_type == "redis"
        assert settings.cache_redis_host == "localhost"
        assert settings.cache_redis_port == 6379
        assert settings.cache_default_timeout == 300

    def test_session_configuration(self):
        """Test session configuration."""
        settings = Settings()
        assert settings.session_type == "redis"
        assert settings.session_cookie_secure is False
        assert settings.session_cookie_httponly is True
        assert settings.session_cookie_samesite == "Lax"

    def test_monitoring_configuration(self):
        """Test monitoring and observability settings."""
        settings = Settings()
        assert settings.prometheus_enabled is True
        assert settings.otel_enabled is False
        assert settings.otel_service_name == "opengov-zoning-api"

    def test_security_headers(self):
        """Test security header configuration."""
        settings = Settings()
        assert settings.csp_default_src == "'self'"
        assert settings.csp_script_src == "'self' 'unsafe-inline'"
        assert settings.csp_style_src == "'self' 'unsafe-inline'"


class TestSettingsSingleton:
    """Test settings singleton functionality."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns a singleton instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_reset_settings(self):
        """Test that settings can be reset."""
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()
        assert settings1 is not settings2

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        settings = Settings()
        original_debug = settings.debug

        # This should not change the settings
        with patch.dict(os.environ, {"DEBUG": "true"}):
            # Create new settings instance
            new_settings = Settings()

        # Original settings should remain unchanged
        assert settings.debug == original_debug
        assert new_settings.debug is True


class TestSettingsValidation:
    """Test settings validation and error handling."""

    def test_invalid_rate_limit_values(self):
        """Test validation of rate limiting values."""
        with patch.dict(os.environ, {"RATE_LIMIT_REQUESTS": "-1"}):
            with pytest.raises(ValueError):
                Settings()

    def test_invalid_port_values(self):
        """Test validation of port values."""
        with patch.dict(os.environ, {"PORT": "not-a-number"}):
            with pytest.raises(ValueError):
                Settings()

    def test_invalid_confidence_threshold(self):
        """Test validation of confidence threshold."""
        with patch.dict(os.environ, {"CONFIDENCE_THRESHOLD": "1.5"}):
            with pytest.raises(ValueError):
                Settings()

    def test_invalid_log_level(self):
        """Test validation of log level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            with pytest.raises(ValueError):
                Settings()


class TestSettingsIntegration:
    """Test settings integration with other components."""

    def test_settings_with_database_manager(self):
        """Test that settings work with database manager."""
        from opengovzoning.core.database import DatabaseManager

        settings = Settings()
        db_manager = DatabaseManager()

        # Should not raise any exceptions
        assert db_manager is not None

    def test_settings_with_redis(self):
        """Test that settings work with Redis configuration."""
        settings = Settings()

        # Should have valid Redis configuration
        assert settings.redis_url.startswith("redis://")
        assert settings.cache_redis_host in settings.redis_url
        assert settings.session_redis_host in settings.redis_url


class TestSettingsPerformance:
    """Test settings performance characteristics."""

    def test_settings_creation_speed(self):
        """Test that settings creation is reasonably fast."""
        import time

        start_time = time.time()
        for _ in range(100):
            Settings()
        end_time = time.time()

        # Should be able to create 100 settings instances in under 1 second
        assert end_time - start_time < 1.0

    def test_settings_memory_usage(self):
        """Test that settings don't use excessive memory."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create multiple settings instances
        settings_list = [Settings() for _ in range(10)]

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 10MB for 10 instances)
        assert memory_increase < 10 * 1024 * 1024