"""External service-related exceptions."""

from typing import Any, Dict, Optional

from fastapi import status

from .base import BaseAPIException


class ExternalServiceError(BaseAPIException):
    """Exception raised for external service failures."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        if details is None:
            details = {}
        details["service_name"] = service_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class RateLimitError(BaseAPIException):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        service_name: str,
        retry_after: Optional[int] = None,
        message: Optional[str] = None,
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Rate limit exceeded for service '{service_name}'"

        if details is None:
            details = {}
        details["service_name"] = service_name
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ServiceUnavailableError(ExternalServiceError):
    """Exception raised when external service is unavailable."""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        error_code: str = "SERVICE_UNAVAILABLE",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Service '{service_name}' is currently unavailable"

        super().__init__(
            service_name=service_name,
            message=message,
            error_code=error_code,
            details=details,
        )


class ExternalAPIError(ExternalServiceError):
    """Exception raised for external API errors."""

    def __init__(
        self,
        service_name: str,
        api_endpoint: str,
        response_status: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        error_code: str = "EXTERNAL_API_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"External API error from '{service_name}' at endpoint '{api_endpoint}'"

        if details is None:
            details = {}
        details["service_name"] = service_name
        details["api_endpoint"] = api_endpoint
        if response_status:
            details["response_status"] = response_status
        if response_body:
            details["response_body"] = response_body

        super().__init__(
            service_name=service_name,
            message=message,
            error_code=error_code,
            details=details,
        )


class TimeoutError(ExternalServiceError):
    """Exception raised when external service requests timeout."""

    def __init__(
        self,
        service_name: str,
        timeout_seconds: int,
        message: Optional[str] = None,
        error_code: str = "TIMEOUT_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Request to '{service_name}' timed out after {timeout_seconds} seconds"

        if details is None:
            details = {}
        details["service_name"] = service_name
        details["timeout_seconds"] = timeout_seconds

        super().__init__(
            service_name=service_name,
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )