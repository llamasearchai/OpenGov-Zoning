"""Base exception classes for OpenGov Zoning API."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class OpenGovZoningException(Exception):
    """Base exception for all OpenGov Zoning application errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "message": self.message,
                "code": self.error_code,
                "details": self.details,
            }
        }


class BaseAPIException(OpenGovZoningException, HTTPException):
    """Base exception for API-related errors that map to HTTP responses."""

    def __init__(
        self,
        message: str,
        error_code: str = "API_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the API exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            status_code: HTTP status code
            headers: Additional headers to include in response
        """
        OpenGovZoningException.__init__(
            self,
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code,
        )
        HTTPException.__init__(
            self,
            status_code=status_code,
            detail=self.to_dict(),
            headers=headers,
        )