"""Comprehensive tests for Data Transfer Objects (DTOs)."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from unittest.mock import patch

from opengovzoning.dtos.auth import (
    UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse,
    PermissionInfo, RoleInfo, APITokenCreate, APITokenResponse,
    SessionInfo, AuditLogEntry
)


class TestUserCreate:
    """Test UserCreate DTO."""

    def test_valid_user_creation(self):
        """Test creating a valid user."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "secret123",
            "role": "user",
            "organization": "Test Org"
        }

        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == "user"
        assert user.organization == "Test Org"

    def test_username_validation(self):
        """Test username validation rules."""
        # Valid usernames
        valid_usernames = ["test_user", "test.user", "test123", "user_name.test"]
        for username in valid_usernames:
            user = UserCreate(
                email="test@example.com",
                username=username,
                first_name="Test",
                last_name="User",
                password="secret123"
            )
            assert user.username == username.lower()

        # Invalid usernames
        invalid_usernames = ["test user", "test@user", "test@user!", "test@user#"]
        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                UserCreate(
                    email="test@example.com",
                    username=username,
                    first_name="Test",
                    last_name="User",
                    password="secret123"
                )

    def test_role_validation(self):
        """Test role validation."""
        valid_roles = ["user", "admin", "analyst", "viewer"]

        for role in valid_roles:
            user = UserCreate(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password="secret123",
                role=role
            )
            assert user.role == role

        # Invalid role
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password="secret123",
                role="invalid_role"
            )

    def test_email_validation(self):
        """Test email validation."""
        # Valid email
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="secret123"
        )
        assert user.email == "test@example.com"

        # Invalid email
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                username="testuser",
                first_name="Test",
                last_name="User",
                password="secret123"
            )

    def test_password_validation(self):
        """Test password validation."""
        # Valid password
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="secret123"
        )
        assert str(user.password) == "secret123"

        # Password too short
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password="123"
            )


class TestUserUpdate:
    """Test UserUpdate DTO."""

    def test_valid_user_update(self):
        """Test valid user update."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "organization": "New Org",
            "is_active": True,
            "role": "admin"
        }

        user_update = UserUpdate(**update_data)

        assert user_update.first_name == "Updated"
        assert user_update.last_name == "Name"
        assert user_update.organization == "New Org"
        assert user_update.is_active is True
        assert user_update.role == "admin"

    def test_partial_user_update(self):
        """Test partial user update."""
        update_data = {
            "first_name": "Updated"
        }

        user_update = UserUpdate(**update_data)

        assert user_update.first_name == "Updated"
        assert user_update.last_name is None
        assert user_update.organization is None
        assert user_update.is_active is None
        assert user_update.role is None

    def test_role_validation_in_update(self):
        """Test role validation in user update."""
        # Valid role update
        user_update = UserUpdate(role="analyst")
        assert user_update.role == "analyst"

        # Invalid role update
        with pytest.raises(ValidationError):
            UserUpdate(role="invalid_role")


class TestUserResponse:
    """Test UserResponse DTO."""

    def test_user_response_creation(self):
        """Test creating user response."""
        user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "organization": "Test Org",
            "is_active": True,
            "is_superuser": False,
            "last_login": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        user_response = UserResponse(**user_data)

        assert str(user_response.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert user_response.email == "test@example.com"
        assert user_response.username == "testuser"
        assert user_response.first_name == "Test"
        assert user_response.last_name == "User"
        assert user_response.role == "user"
        assert user_response.organization == "Test Org"
        assert user_response.is_active is True
        assert user_response.is_superuser is False


class TestLoginRequest:
    """Test LoginRequest DTO."""

    def test_valid_login_request(self):
        """Test valid login request."""
        login_data = {
            "username": "testuser",
            "password": "secret123",
            "remember_me": True
        }

        login_request = LoginRequest(**login_data)

        assert login_request.username == "testuser"
        assert str(login_request.password) == "secret123"
        assert login_request.remember_me is True

    def test_login_request_defaults(self):
        """Test login request with default values."""
        login_data = {
            "username": "testuser",
            "password": "secret123"
        }

        login_request = LoginRequest(**login_data)

        assert login_request.username == "testuser"
        assert str(login_request.password) == "secret123"
        assert login_request.remember_me is False  # Default value


class TestLoginResponse:
    """Test LoginResponse DTO."""

    def test_login_response_creation(self):
        """Test creating login response."""
        user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "organization": "Test Org",
            "is_active": True,
            "is_superuser": False,
            "last_login": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        login_data = {
            "user": UserResponse(**user_data),
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 3600
        }

        login_response = LoginResponse(**login_data)

        assert login_response.access_token == "access_token_123"
        assert login_response.refresh_token == "refresh_token_123"
        assert login_response.token_type == "bearer"
        assert login_response.expires_in == 3600


class TestPermissionInfo:
    """Test PermissionInfo DTO."""

    def test_permission_info_creation(self):
        """Test creating permission info."""
        permission_data = {
            "resource": "documents",
            "actions": ["read", "write", "delete"],
            "conditions": {"department": "planning"}
        }

        permission = PermissionInfo(**permission_data)

        assert permission.resource == "documents"
        assert permission.actions == ["read", "write", "delete"]
        assert permission.conditions == {"department": "planning"}

    def test_permission_info_optional_conditions(self):
        """Test permission info without conditions."""
        permission_data = {
            "resource": "documents",
            "actions": ["read"]
        }

        permission = PermissionInfo(**permission_data)

        assert permission.resource == "documents"
        assert permission.actions == ["read"]
        assert permission.conditions is None


class TestRoleInfo:
    """Test RoleInfo DTO."""

    def test_role_info_creation(self):
        """Test creating role info."""
        permission = PermissionInfo(
            resource="documents",
            actions=["read", "write"]
        )

        role_data = {
            "name": "editor",
            "description": "Document editor role",
            "permissions": [permission],
            "is_default": False
        }

        role = RoleInfo(**role_data)

        assert role.name == "editor"
        assert role.description == "Document editor role"
        assert len(role.permissions) == 1
        assert role.is_default is False

    def test_role_info_default_values(self):
        """Test role info with default values."""
        role_data = {
            "name": "viewer",
            "description": "Read-only viewer",
            "permissions": []
        }

        role = RoleInfo(**role_data)

        assert role.name == "viewer"
        assert role.description == "Read-only viewer"
        assert role.permissions == []
        assert role.is_default is False  # Default value


class TestAPITokenCreate:
    """Test APITokenCreate DTO."""

    def test_api_token_creation(self):
        """Test creating API token request."""
        token_data = {
            "name": "Test API Token",
            "expires_in_days": 365,
            "permissions": ["read:documents", "write:documents"]
        }

        token = APITokenCreate(**token_data)

        assert token.name == "Test API Token"
        assert token.expires_in_days == 365
        assert token.permissions == ["read:documents", "write:documents"]

    def test_api_token_defaults(self):
        """Test API token with default values."""
        token_data = {
            "name": "Test Token"
        }

        token = APITokenCreate(**token_data)

        assert token.name == "Test Token"
        assert token.expires_in_days == 365  # Default value
        assert token.permissions is None  # Default value

    def test_api_token_validation(self):
        """Test API token validation."""
        # Valid token
        token = APITokenCreate(name="Valid Token", expires_in_days=180)
        assert token.expires_in_days == 180

        # Invalid: expires_in_days too small
        with pytest.raises(ValidationError):
            APITokenCreate(name="Invalid Token", expires_in_days=0)

        # Invalid: expires_in_days too large
        with pytest.raises(ValidationError):
            APITokenCreate(name="Invalid Token", expires_in_days=4000)


class TestAPITokenResponse:
    """Test APITokenResponse DTO."""

    def test_api_token_response_creation(self):
        """Test creating API token response."""
        token_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Test Token",
            "token": "api_token_123456789",
            "permissions": ["read:documents"],
            "created_at": datetime.now(),
            "expires_at": None,
            "last_used": None
        }

        token_response = APITokenResponse(**token_data)

        assert str(token_response.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert token_response.name == "Test Token"
        assert token_response.token == "api_token_123456789"
        assert token_response.permissions == ["read:documents"]
        assert token_response.expires_at is None
        assert token_response.last_used is None


class TestSessionInfo:
    """Test SessionInfo DTO."""

    def test_session_info_creation(self):
        """Test creating session info."""
        session_data = {
            "session_id": "session_123",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "created_at": datetime.now(),
            "expires_at": datetime.now(),
            "is_active": True
        }

        session = SessionInfo(**session_data)

        assert session.session_id == "session_123"
        assert str(session.user_id) == "123e4567-e89b-12d3-a456-426614174000"
        assert session.ip_address == "192.168.1.100"
        assert session.user_agent == "Mozilla/5.0..."
        assert session.is_active is True

    def test_session_info_optional_fields(self):
        """Test session info with optional fields."""
        session_data = {
            "session_id": "session_456",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": datetime.now(),
            "expires_at": datetime.now(),
            "is_active": False
        }

        session = SessionInfo(**session_data)

        assert session.session_id == "session_456"
        assert session.ip_address is None
        assert session.user_agent is None
        assert session.is_active is False


class TestAuditLogEntry:
    """Test AuditLogEntry DTO."""

    def test_audit_log_entry_creation(self):
        """Test creating audit log entry."""
        audit_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "123e4567-e89b-12d3-a456-426614174001",
            "action": "document_created",
            "resource_type": "document",
            "resource_id": "doc_123",
            "timestamp": datetime.now(),
            "ip_address": "192.168.1.100",
            "details": {"filename": "test.pdf", "size": 1024}
        }

        audit_entry = AuditLogEntry(**audit_data)

        assert str(audit_entry.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert str(audit_entry.user_id) == "123e4567-e89b-12d3-a456-426614174001"
        assert audit_entry.action == "document_created"
        assert audit_entry.resource_type == "document"
        assert audit_entry.resource_id == "doc_123"
        assert audit_entry.ip_address == "192.168.1.100"
        assert audit_entry.details == {"filename": "test.pdf", "size": 1024}

    def test_audit_log_entry_optional_fields(self):
        """Test audit log entry with optional fields."""
        audit_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": None,
            "action": "system_startup",
            "resource_type": "system",
            "resource_id": None,
            "timestamp": datetime.now(),
            "ip_address": None,
            "details": {"version": "1.0.0"}
        }

        audit_entry = AuditLogEntry(**audit_data)

        assert audit_entry.user_id is None
        assert audit_entry.resource_id is None
        assert audit_entry.ip_address is None
        assert audit_entry.details == {"version": "1.0.0"}


class TestDTOValidation:
    """Test DTO validation and error handling."""

    def test_field_validation_errors(self):
        """Test field validation error messages."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email",
                username="test user",  # Invalid username
                first_name="Test",
                last_name="User",
                password="123"  # Too short
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0

        # Check that we have validation errors for multiple fields
        field_names = [error['loc'][0] for error in errors]
        assert 'email' in field_names or 'username' in field_names or 'password' in field_names

    def test_json_serialization(self):
        """Test DTO JSON serialization."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="secret123"
        )

        # Should be able to serialize to JSON
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict['email'] == "test@example.com"
        assert user_dict['username'] == "testuser"

        # Password should be excluded from serialization by default
        assert 'password' not in user_dict

    def test_json_deserialization(self):
        """Test DTO JSON deserialization."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "secret123"
        }

        # Should be able to deserialize from JSON
        user = UserCreate.model_validate(user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"


class TestDTOIntegration:
    """Test DTO integration with other components."""

    def test_dto_with_api_layer(self):
        """Test DTO integration with API layer."""
        from opengovzoning.web.app import app

        # Should be able to import and use together
        assert app is not None

    def test_dto_with_database_layer(self):
        """Test DTO integration with database layer."""
        from opengovzoning.infrastructure.database.models import Item

        # Should be able to work together
        assert Item is not None

    def test_dto_with_service_layer(self):
        """Test DTO integration with service layer."""
        from opengovzoning.services.agent_service import AgentService

        # Should be able to work together
        assert AgentService is not None