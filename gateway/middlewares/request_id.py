"""
Request ID middleware module.

This module provides request ID generation and propagation for distributed
tracing across the API gateway and its upstream services.
"""

import uuid
from typing import Union
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from contextvars import ContextVar


# Context variable for request ID (works with async context)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and propagate request IDs.

    This middleware assigns a unique request ID to each incoming request,
    either extracting it from the X-Request-ID header (if present) or
    generating a new UUID. The request ID is stored in a context variable
    for use throughout the request lifecycle and is added to response headers
    for traceability.

    Attributes:
        header_name: The name of the header to use for request ID.
            Defaults to "X-Request-ID".

    Example:
        >>> app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        """
        Initialize the RequestIDMiddleware.

        Args:
            app: The ASGI application to wrap.
            header_name: The name of the header to extract/request ID from.
                Defaults to "X-Request-ID".
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Response:
        """
        Process the request and assign/forward request ID.

        Args:
            request: The incoming FastAPI Request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The response from the next handler with request ID header.
        """
        # Extract request ID from header or generate new one
        request_id: str = request.headers.get(self.header_name) or str(uuid.uuid4())

        # Store in context variable for use throughout request lifecycle
        request_id_var.set(request_id)

        # Process the request
        response: Response = await call_next(request)

        # Add request ID to response headers
        response.headers[self.header_name] = request_id

        return response


def get_request_id() -> str:
    """
    Get the current request ID from the context.

    This function retrieves the request ID set by the RequestIDMiddleware
    for the current request context. If no request ID is set (e.g., outside
    of a request context), an empty string is returned.

    Returns:
        str: The current request ID, or empty string if not set.

    Example:
        >>> request_id = get_request_id()
        >>> print(f"Processing request: {request_id}")
    """
    return request_id_var.get()
