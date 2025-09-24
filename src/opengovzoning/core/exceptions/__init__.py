"""Custom exceptions for OpenGov Zoning API."""

from .base import BaseAPIException, OpenGovZoningException
from .auth import AuthenticationError, AuthorizationError, TokenError
from .database import DatabaseError, RecordNotFoundError, DuplicateRecordError
from .validation import ValidationError, InvalidInputError
from .external import ExternalServiceError, RateLimitError
from .business import BusinessLogicError, InsufficientPermissionsError

__all__ = [
    # Base exceptions
    "BaseAPIException",
    "OpenGovZoningException",

    # Authentication & Authorization
    "AuthenticationError",
    "AuthorizationError",
    "TokenError",

    # Database
    "DatabaseError",
    "RecordNotFoundError",
    "DuplicateRecordError",

    # Validation
    "ValidationError",
    "InvalidInputError",

    # External services
    "ExternalServiceError",
    "RateLimitError",

    # Business logic
    "BusinessLogicError",
    "InsufficientPermissionsError",
]