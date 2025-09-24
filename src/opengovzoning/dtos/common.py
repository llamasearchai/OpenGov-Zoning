"""Common Data Transfer Objects for OpenGov Zoning API."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    offset: Optional[int] = Field(default=None, ge=0, description="Number of items to skip")

    @field_validator("offset", mode="before")
    @classmethod
    def calculate_offset(cls, v, info):
        """Calculate offset from page and size if not provided."""
        if v is not None:
            return v
        page = info.data.get("page", 1) if info.data else 1
        size = info.data.get("size", 20) if info.data else 20
        return (page - 1) * size


class SortParams(BaseModel):
    """Sorting parameters for list endpoints."""

    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort_by field name."""
        if v and not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("Invalid sort field name")
        return v


class FilterParams(BaseModel):
    """Filtering parameters for list endpoints."""

    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Field filters")

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v):
        """Validate filter values."""
        for key, value in v.items():
            if not key.replace("_", "").replace(".", "").isalnum():
                raise ValueError(f"Invalid filter field name: {key}")
        return v


class SearchParams(BaseModel):
    """Search parameters for list endpoints."""

    query: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Search query")
    search_fields: Optional[List[str]] = Field(default=None, description="Fields to search in")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response from items and pagination info."""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class APIResponse(BaseModel):
    """Generic API response model."""

    success: bool = Field(default=True, description="Request success status")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "Request completed successfully"
    ) -> "APIResponse":
        """Create success response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(
        cls,
        message: str = "Request failed",
        data: Any = None
    ) -> "APIResponse":
        """Create error response."""
        return cls(success=False, message=message, data=data)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")

    @classmethod
    def create(
        cls,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "ErrorResponse":
        """Create error response."""
        return cls(
            error={
                "message": message,
                "code": code,
                "details": details or {},
            },
            request_id=request_id,
        )


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error: Dict[str, Any] = Field(..., description="Validation error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")

    @classmethod
    def create(
        cls,
        field_errors: List[Dict[str, Any]],
        message: str = "Validation failed",
        request_id: Optional[str] = None,
    ) -> "ValidationErrorResponse":
        """Create validation error response."""
        return cls(
            error={
                "message": message,
                "code": "VALIDATION_ERROR",
                "field_errors": field_errors,
            },
            request_id=request_id,
        )


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime: Optional[float] = Field(default=None, description="Service uptime in seconds")
    database_status: str = Field(default="unknown", description="Database connection status")
    redis_status: str = Field(default="unknown", description="Redis connection status")


class MetricsResponse(BaseModel):
    """Metrics response model."""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    metrics: Dict[str, Any] = Field(..., description="System metrics")


class VersionResponse(BaseModel):
    """Version information response model."""

    version: str = Field(..., description="Application version")
    build_date: Optional[str] = Field(default=None, description="Build date")
    git_commit: Optional[str] = Field(default=None, description="Git commit hash")
    environment: str = Field(..., description="Deployment environment")


class LocationInfo(BaseModel):
    """Location information model."""

    address: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State/Province")
    zip_code: Optional[str] = Field(default=None, description="ZIP/Postal code")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude")
    geometry: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON geometry")


class ContactInfo(BaseModel):
    """Contact information model."""

    name: str = Field(..., description="Contact name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone")
    organization: Optional[str] = Field(default=None, description="Contact organization")


class MetadataInfo(BaseModel):
    """Metadata information model."""

    created_by: Optional[str] = Field(default=None, description="Created by user")
    updated_by: Optional[str] = Field(default=None, description="Updated by user")
    tags: List[str] = Field(default_factory=list, description="Resource tags")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")