"""
Custom exceptions module for the API Gateway.

This module defines standardized exception classes and error response
models for consistent error handling across the gateway.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    """
    Standardized error codes for the API gateway.

    These codes provide consistent error identification across all
    gateway operations and are used in ErrorResponse objects.

    Categories:
        - Authentication/Authorization errors
        - Request validation errors
        - Gateway errors
        - Internal errors
    """

    # Authentication/Authorization
    AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"

    # Request errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUEST_TOO_LARGE = "REQUEST_TOO_LARGE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Gateway errors
    UPSTREAM_TIMEOUT = "UPSTREAM_TIMEOUT"
    UPSTREAM_UNAVAILABLE = "UPSTREAM_UNAVAILABLE"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"

    # Internal errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class ErrorResponse(BaseModel):
    """
    Standardized error response format.

    This model provides a consistent structure for all error responses
    returned by the gateway, including error code, message, timestamp,
    and optional details.

    Attributes:
        error: The error type (default: "error").
        code: The ErrorCode enum value.
        message: Human-readable error message.
        timestamp: ISO format timestamp of when the error occurred.
        request_id: The request ID for tracing (optional).
        path: The request path that caused the error (optional).
        details: Additional error details (optional).

    Example:
        >>> error_response = ErrorResponse(
        ...     code=ErrorCode.UPSTREAM_UNAVAILABLE,
        ...     message="Backend service is unavailable",
        ...     request_id="abc-123",
        ...     path="/api/v1/users"
        ... )
    """

    error: str = "error"
    code: ErrorCode
    message: str
    timestamp: str = datetime.utcnow().isoformat()
    request_id: Optional[str] = None
    path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class GatewayException(Exception):
    """
    Base exception for gateway errors.

    This is the base class for all custom exceptions raised by the
    gateway. It provides structured error information including
    error code, message, HTTP status code, and additional details.

    Attributes:
        code: The ErrorCode enum value.
        message: Human-readable error message.
        status_code: HTTP status code to return.
        details: Additional error details dictionary.
        path: The request path that caused the error.

    Example:
        >>> raise GatewayException(
        ...     code=ErrorCode.UPSTREAM_TIMEOUT,
        ...     message="Backend service timed out",
        ...     status_code=504,
        ...     details={"upstream": "users-service"}
        ... )
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None
    ) -> None:
        """
        Initialize a GatewayException.

        Args:
            code: The ErrorCode enum value.
            message: Human-readable error description.
            status_code: HTTP status code (default: 500).
            details: Additional context about the error (optional).
            path: Request path that caused the error (optional).
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.path = path
        super().__init__(self.message)


class RateLimitExceededException(GatewayException):
    """
    Exception raised when rate limit is exceeded.

    This exception is raised when a client exceeds the configured
    rate limit and should be throttled.

    Attributes:
        message: Human-readable error message.
        retry_after: Seconds until the client can retry (default: 60).

    Example:
        >>> raise RateLimitExceededException(
        ...     message="Too many requests",
        ...     retry_after=120
        ... )
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60
    ) -> None:
        """
        Initialize a RateLimitExceededException.

        Args:
            message: Error message (default: "Rate limit exceeded").
            retry_after: Seconds until retry is allowed (default: 60).
        """
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            status_code=429,
            details={"retry_after": retry_after}
        )


class UpstreamServiceException(GatewayException):
    """
    Exception raised when an upstream service error occurs.

    This exception is raised when communicating with a backend
    service fails or returns an unexpected error.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code from upstream service.
        upstream_code: Error code from the upstream service.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        upstream_code: str
    ) -> None:
        """
        Initialize an UpstreamServiceException.

        Args:
            message: Error message describing the upstream failure.
            status_code: HTTP status code from upstream.
            upstream_code: Error code from the upstream service.
        """
        super().__init__(
            code=ErrorCode.UPSTREAM_ERROR,
            message=message,
            status_code=status_code,
            details={"upstream_error_code": upstream_code}
        )
