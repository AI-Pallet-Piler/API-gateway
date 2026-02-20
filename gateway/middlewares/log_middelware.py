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
from gateway.loggers.logger import create_logger

# Create logger for this module
logger = create_logger("gateway.middlewares.log")


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

        # Get request ID for tracing
        from gateway.middlewares.request_id import get_request_id
        request_id = get_request_id() or "N/A"

        # Log request details
        logger.info(
            "Incoming request",
            extra={
                "event": "request_start",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            }
        )

        # Process the request
        response: Response = await call_next(request)

        # Calculate duration
        duration: float = time.time() - start_time

        # Log response details
        logger.info(
            "Request completed",
            extra={
                "event": "request_end",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )

        # Record metrics
        MetricsMiddleware.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )

        return response
