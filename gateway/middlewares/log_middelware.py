"""
Logging middleware module for request/response logging.

This middleware logs request details and response metrics including
method, path, status code, and duration for monitoring purposes.
"""

import time
from typing import Union
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from gateway.routes.metrics import MetricsMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP request/response metrics.

    This middleware intercepts requests, measures the processing time,
    and records metrics using the MetricsMiddleware. It provides
    visibility into request patterns and performance.

    Attributes:
        None (configuration is handled by MetricsMiddleware)

    Example:
        >>> app.add_middleware(LoggingMiddleware)
    """

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Union[Response, Exception]:
        """
        Process the request and record metrics.

        Args:
            request: The incoming Starlette Request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The response from the next handler.

        Raises:
            Exception: Any exception raised by downstream handlers.
        """
        start_time: float = time.time()

        # Process the request
        response: Response = await call_next(request)

        # Calculate duration
        duration: float = time.time() - start_time

        # Record metrics
        MetricsMiddleware.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )

        return response
