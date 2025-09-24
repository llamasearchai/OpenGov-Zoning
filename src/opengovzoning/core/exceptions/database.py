"""Database-related exceptions."""

from typing import Any, Dict, Optional

from fastapi import status

from .base import BaseAPIException


class DatabaseError(BaseAPIException):
    """Exception raised for database-related errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RecordNotFoundError(DatabaseError):
    """Exception raised when a requested record is not found."""

    def __init__(
        self,
        resource: str = "record",
        identifier: Optional[str] = None,
        message: Optional[str] = None,
        error_code: str = "RECORD_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if identifier:
                message = f"{resource.capitalize()} with identifier '{identifier}' not found"
            else:
                message = f"{resource.capitalize()} not found"

        if details is None:
            details = {}
        if identifier:
            details["identifier"] = identifier
        details["resource"] = resource

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateRecordError(DatabaseError):
    """Exception raised when attempting to create a record that already exists."""

    def __init__(
        self,
        resource: str = "record",
        field: str = "identifier",
        value: Optional[str] = None,
        message: Optional[str] = None,
        error_code: str = "DUPLICATE_RECORD",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if value:
                message = f"{resource.capitalize()} with {field} '{value}' already exists"
            else:
                message = f"{resource.capitalize()} already exists"

        if details is None:
            details = {}
        details["resource"] = resource
        details["field"] = field
        if value:
            details["value"] = value

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_409_CONFLICT,
        )


class DatabaseConnectionError(DatabaseError):
    """Exception raised for database connection issues."""

    def __init__(
        self,
        message: str = "Database connection failed",
        error_code: str = "DATABASE_CONNECTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class DatabaseTimeoutError(DatabaseError):
    """Exception raised for database timeout issues."""

    def __init__(
        self,
        message: str = "Database operation timed out",
        error_code: str = "DATABASE_TIMEOUT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class TransactionError(DatabaseError):
    """Exception raised for database transaction issues."""

    def __init__(
        self,
        message: str = "Database transaction failed",
        error_code: str = "TRANSACTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )