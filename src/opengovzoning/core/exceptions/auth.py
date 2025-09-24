"""Authentication and authorization exceptions."""

from typing import Any, Dict, Optional

from fastapi import status

from .base import BaseAPIException


class AuthenticationError(BaseAPIException):
    """Exception raised for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(BaseAPIException):
    """Exception raised for authorization failures."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class TokenError(BaseAPIException):
    """Exception raised for JWT token-related errors."""

    def __init__(
        self,
        message: str = "Token validation failed",
        error_code: str = "TOKEN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenError(TokenError):
    """Exception raised for invalid or malformed tokens."""

    def __init__(
        self,
        message: str = "Invalid token",
        error_code: str = "INVALID_TOKEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ExpiredTokenError(TokenError):
    """Exception raised for expired tokens."""

    def __init__(
        self,
        message: str = "Token has expired",
        error_code: str = "EXPIRED_TOKEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InsufficientPermissionsError(AuthorizationError):
    """Exception raised when user lacks required permissions."""

    def __init__(
        self,
        required_permissions: Optional[list] = None,
        user_permissions: Optional[list] = None,
        message: Optional[str] = None,
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = "Insufficient permissions for this operation"

        if details is None:
            details = {}

        if required_permissions:
            details["required_permissions"] = required_permissions
        if user_permissions:
            details["user_permissions"] = user_permissions

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )