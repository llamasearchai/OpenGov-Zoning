"""Validation-related exceptions."""

from typing import Any, Dict, List, Optional

from fastapi import status

from .base import BaseAPIException


class ValidationError(BaseAPIException):
    """Exception raised for input validation failures."""

    def __init__(
        self,
        message: str = "Input validation failed",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        field_errors: Optional[List[Dict[str, Any]]] = None,
    ):
        if details is None:
            details = {}
        if field_errors:
            details["field_errors"] = field_errors

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class InvalidInputError(ValidationError):
    """Exception raised for invalid input data."""

    def __init__(
        self,
        message: str = "Invalid input provided",
        error_code: str = "INVALID_INPUT",
        details: Optional[Dict[str, Any]] = None,
        field_errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            field_errors=field_errors,
        )


class MissingRequiredFieldError(InvalidInputError):
    """Exception raised when required fields are missing."""

    def __init__(
        self,
        field_name: str,
        message: Optional[str] = None,
        error_code: str = "MISSING_REQUIRED_FIELD",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Required field '{field_name}' is missing"

        if details is None:
            details = {}
        details["field_name"] = field_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )


class InvalidFormatError(InvalidInputError):
    """Exception raised when input format is invalid."""

    def __init__(
        self,
        field_name: str,
        expected_format: str,
        actual_value: Optional[str] = None,
        message: Optional[str] = None,
        error_code: str = "INVALID_FORMAT",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Field '{field_name}' has invalid format. Expected: {expected_format}"

        if details is None:
            details = {}
        details["field_name"] = field_name
        details["expected_format"] = expected_format
        if actual_value:
            details["actual_value"] = actual_value

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )


class ValueOutOfRangeError(InvalidInputError):
    """Exception raised when a value is outside the acceptable range."""

    def __init__(
        self,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        actual_value: Optional[float] = None,
        message: Optional[str] = None,
        error_code: str = "VALUE_OUT_OF_RANGE",
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if min_value is not None and max_value is not None:
                message = f"Field '{field_name}' value must be between {min_value} and {max_value}"
            elif min_value is not None:
                message = f"Field '{field_name}' value must be at least {min_value}"
            elif max_value is not None:
                message = f"Field '{field_name}' value must be at most {max_value}"
            else:
                message = f"Field '{field_name}' value is out of range"

        if details is None:
            details = {}
        details["field_name"] = field_name
        if min_value is not None:
            details["min_value"] = min_value
        if max_value is not None:
            details["max_value"] = max_value
        if actual_value is not None:
            details["actual_value"] = actual_value

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )