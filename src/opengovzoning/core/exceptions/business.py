"""Business logic-related exceptions."""

from typing import Any, Dict, Optional

from fastapi import status

from .base import BaseAPIException


class BusinessLogicError(BaseAPIException):
    """Exception raised for business logic violations."""

    def __init__(
        self,
        message: str = "Business logic error",
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InsufficientPermissionsError(BusinessLogicError):
    """Exception raised when user lacks required permissions for business operation."""

    def __init__(
        self,
        operation: str,
        required_permissions: Optional[list] = None,
        user_permissions: Optional[list] = None,
        message: Optional[str] = None,
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Insufficient permissions to perform operation: {operation}"

        if details is None:
            details = {}
        details["operation"] = operation
        if required_permissions:
            details["required_permissions"] = required_permissions
        if user_permissions:
            details["user_permissions"] = user_permissions

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )


class ResourceConflictError(BusinessLogicError):
    """Exception raised when there's a conflict with existing resources."""

    def __init__(
        self,
        resource: str,
        conflict_reason: str,
        message: Optional[str] = None,
        error_code: str = "RESOURCE_CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Resource conflict for {resource}: {conflict_reason}"

        if details is None:
            details = {}
        details["resource"] = resource
        details["conflict_reason"] = conflict_reason

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidStateError(BusinessLogicError):
    """Exception raised when an operation is attempted in an invalid state."""

    def __init__(
        self,
        resource: str,
        current_state: str,
        required_state: Optional[str] = None,
        message: Optional[str] = None,
        error_code: str = "INVALID_STATE",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if required_state:
                message = f"Invalid state for {resource}: current='{current_state}', required='{required_state}'"
            else:
                message = f"Invalid state for {resource}: {current_state}"

        if details is None:
            details = {}
        details["resource"] = resource
        details["current_state"] = current_state
        if required_state:
            details["required_state"] = required_state

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )


class QuotaExceededError(BusinessLogicError):
    """Exception raised when user or system quotas are exceeded."""

    def __init__(
        self,
        quota_type: str,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        message: Optional[str] = None,
        error_code: str = "QUOTA_EXCEEDED",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if current_usage is not None and quota_limit is not None:
                message = f"{quota_type} quota exceeded: {current_usage}/{quota_limit}"
            else:
                message = f"{quota_type} quota exceeded"

        if details is None:
            details = {}
        details["quota_type"] = quota_type
        if current_usage is not None:
            details["current_usage"] = current_usage
        if quota_limit is not None:
            details["quota_limit"] = quota_limit

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )