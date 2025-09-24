"""Authentication and authorization Data Transfer Objects."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator, ConfigDict

from .common import ContactInfo


class UserCreate(BaseModel):
    """User creation request model."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    password: SecretStr = Field(..., min_length=8, description="Password")
    role: str = Field(default="user", description="User role")
    organization: Optional[str] = Field(default=None, max_length=255, description="Organization")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, dots, and underscores")
        return v.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate user role."""
        valid_roles = ["user", "admin", "analyst", "viewer"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class UserUpdate(BaseModel):
    """User update request model."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Last name")
    organization: Optional[str] = Field(default=None, max_length=255, description="Organization")
    is_active: Optional[bool] = Field(default=None, description="Account active status")
    role: Optional[str] = Field(default=None, description="User role")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate user role."""
        if v is not None:
            valid_roles = ["user", "admin", "analyst", "viewer"]
            if v not in valid_roles:
                raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class UserResponse(BaseModel):
    """User response model."""

    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    organization: Optional[str]
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., description="Username or email")
    password: SecretStr = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Remember login")


class LoginResponse(BaseModel):
    """Login response model."""

    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request model."""

    token: str = Field(..., description="Reset token")
    new_password: SecretStr = Field(..., min_length=8, description="New password")


class ChangePasswordRequest(BaseModel):
    """Change password request model."""

    current_password: SecretStr = Field(..., description="Current password")
    new_password: SecretStr = Field(..., min_length=8, description="New password")


class PermissionInfo(BaseModel):
    """Permission information model."""

    resource: str
    actions: List[str]
    conditions: Optional[Dict] = None


class RoleInfo(BaseModel):
    """Role information model."""

    name: str
    description: str
    permissions: List[PermissionInfo]
    is_default: bool = False


class APITokenCreate(BaseModel):
    """API token creation request model."""

    name: str = Field(..., min_length=1, max_length=100, description="Token name")
    expires_in_days: Optional[int] = Field(default=365, ge=1, le=3650, description="Token expiration in days")
    permissions: Optional[List[str]] = Field(default=None, description="Token permissions")


class APITokenResponse(BaseModel):
    """API token response model."""

    id: UUID
    name: str
    token: str  # Only shown on creation
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SessionInfo(BaseModel):
    """User session information model."""

    session_id: str
    user_id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_active: bool


class AuditLogEntry(BaseModel):
    """Audit log entry model."""

    id: UUID
    user_id: Optional[UUID]
    action: str
    resource_type: str
    resource_id: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    details: Dict

    model_config = ConfigDict(from_attributes=True)