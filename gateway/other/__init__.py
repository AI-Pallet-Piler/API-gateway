"""
Other utilities module for the API Gateway.

This module provides additional utilities including:
    exceptions: Custom exception classes for the gateway.

Custom Exceptions:
    GatewayException: Base exception for all gateway errors.
    UpstreamException: Exception for upstream service errors.
    AuthenticationException: Exception for authentication errors.

Usage:
    >>> from gateway.other.exceptions import GatewayException
    >>> raise GatewayException("Something went wrong")
"""

from . import exceptions

__all__ = [
    "exceptions"
]
