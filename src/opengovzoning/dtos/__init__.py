"""Data Transfer Objects for OpenGov Zoning API."""

from .auth import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
)
from .project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectSummary,
)
from .analysis import (
    ZoningAnalysisCreate,
    ZoningAnalysisUpdate,
    ZoningAnalysisResponse,
    AnalysisResult,
    Recommendation,
)
from .document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentUploadResponse,
    DocumentMetadata,
)
from .common import (
    PaginationParams,
    PaginatedResponse,
    SortParams,
    FilterParams,
    SearchParams,
    APIResponse,
    ErrorResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Authentication DTOs
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirmRequest",

    # Project DTOs
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectSummary",

    # Analysis DTOs
    "ZoningAnalysisCreate",
    "ZoningAnalysisUpdate",
    "ZoningAnalysisResponse",
    "AnalysisResult",
    "Recommendation",

    # Document DTOs
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentMetadata",

    # Common DTOs
    "PaginationParams",
    "PaginatedResponse",
    "SortParams",
    "FilterParams",
    "SearchParams",
    "APIResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
]