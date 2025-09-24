"""Production-ready configuration management for OpenGov Zoning API."""

import secrets
from typing import List, Optional, Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Production-ready application settings for OpenGov Zoning API."""

    # Application Settings
    app_name: str = "OpenGov Zoning API"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=True, env="RELOAD")

    # Database Configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./opengov_zoning.db",
        env="DATABASE_URL"
    )
    demo_sqlite_path: str = Field(
        default="./data/opengov_zoning_demo.db",
        env="DEMO_SQLITE_PATH",
    )

    # Database Pool Settings
    db_pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_cache_ttl: int = Field(default=3600, env="REDIS_CACHE_TTL")

    # Authentication & Security
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # OAuth2 Configuration
    oauth2_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="OAUTH2_SECRET_KEY")
    oauth2_token_url: str = Field(default="https://example.com/token", env="OAUTH2_TOKEN_URL")
    oauth2_authorization_url: str = Field(default="https://example.com/auth", env="OAUTH2_AUTHORIZATION_URL")

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")

    # GIS Configuration
    gis_api_base: str = Field(default="https://gis.company.com/api", env="GIS_API_BASE")
    gis_api_key: Optional[str] = Field(default=None, env="GIS_API_KEY")

    # Email Configuration
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    email_from: str = Field(default="noreply@opengovzoning.com", env="EMAIL_FROM")

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    supported_formats: str = Field(default="pdf,docx,txt,html,xml", env="SUPPORTED_FORMATS")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str = Field(default="./logs/opengov_zoning.log", env="LOG_FILE")

    # Monitoring & Observability
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    otel_enabled: bool = Field(default=False, env="OTEL_ENABLED")
    otel_service_name: str = Field(default="opengov-zoning-api", env="OTEL_SERVICE_NAME")

    # CORS Settings (secure defaults)
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: ["Content-Type", "Authorization", "X-Requested-With"],
        env="CORS_ALLOW_HEADERS"
    )

    # Security Headers
    csp_default_src: str = Field(default="'self'", env="CSP_DEFAULT_SRC")
    csp_script_src: str = Field(default="'self' 'unsafe-inline'", env="CSP_SCRIPT_SRC")
    csp_style_src: str = Field(default="'self' 'unsafe-inline'", env="CSP_STYLE_SRC")

    # Feature Flags
    enable_registration: bool = Field(default=True, env="ENABLE_REGISTRATION")
    enable_file_upload: bool = Field(default=True, env="ENABLE_FILE_UPLOAD")
    enable_gis_integration: bool = Field(default=True, env="ENABLE_GIS_INTEGRATION")
    enable_email_notifications: bool = Field(default=True, env="ENABLE_EMAIL_NOTIFICATIONS")

    # Performance Settings
    max_concurrent_analyses: int = Field(default=5, env="MAX_CONCURRENT_ANALYSES")
    confidence_threshold: float = Field(default=0.85, env="CONFIDENCE_THRESHOLD")
    max_document_size_mb: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")

    # Cache Settings
    cache_type: str = Field(default="redis", env="CACHE_TYPE")
    cache_redis_host: str = Field(default="localhost", env="CACHE_REDIS_HOST")
    cache_redis_port: int = Field(default=6379, env="CACHE_REDIS_PORT")
    cache_redis_db: int = Field(default=0, env="CACHE_REDIS_DB")
    cache_default_timeout: int = Field(default=300, env="CACHE_DEFAULT_TIMEOUT")

    # Session Configuration
    session_type: str = Field(default="redis", env="SESSION_TYPE")
    session_redis_host: str = Field(default="localhost", env="SESSION_REDIS_HOST")
    session_redis_port: int = Field(default=6379, env="SESSION_REDIS_PORT")
    session_redis_db: int = Field(default=1, env="SESSION_REDIS_DB")
    session_cookie_secure: bool = Field(default=False, env="SESSION_COOKIE_SECURE")
    session_cookie_httponly: bool = Field(default=True, env="SESSION_COOKIE_HTTPONLY")
    session_cookie_samesite: str = Field(default="Lax", env="SESSION_COOKIE_SAMESITE")

    # Testing Configuration
    test_database_url: str = Field(
        default="sqlite+aiosqlite:///./test.db",
        env="TEST_DATABASE_URL"
    )
    test_redis_url: str = Field(default="redis://localhost:6379/1", env="TEST_REDIS_URL")

    # Documentation
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8"
    }

    @field_validator("cors_origins")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("cors_allow_methods", "cors_allow_headers")
    @classmethod
    def assemble_cors_headers(cls, v: str | List[str]) -> List[str]:
        """Parse CORS methods/headers from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env.lower() == "test"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset settings singleton (useful for testing)."""
    global _settings
    _settings = None