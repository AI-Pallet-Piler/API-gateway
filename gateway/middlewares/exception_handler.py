"""
Exception handler middleware module.

This module provides centralized exception handling for the API gateway,
ensuring consistent error responses and proper logging of all exceptions.
"""

import logging
from typing import Union
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from gateway.other.exceptions import GatewayException, ErrorResponse, ErrorCode
from gateway.middlewares.request_id import get_request_id


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions consistently.

    This middleware catches all exceptions raised during request processing
    and converts them into standardized JSON error responses. It handles
    GatewayException subclasses specially, while unexpected exceptions
    are logged as critical errors.

    Attributes:
        None (configuration via exception classes)

    Example:
        >>> app.add_middleware(ExceptionHandlingMiddleware)
    """

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Union[Response, JSONResponse]:
        """
        Process the request and handle any exceptions.

        Args:
            request: The incoming FastAPI Request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The response from the next handler if no exception.
            JSONResponse: A standardized error response if exception occurs.

        Raises:
            GatewayException: Will be caught and converted to JSON response.
            Exception: Will be caught and converted to internal error response.
        """
        try:
            response = await call_next(request)
            return response
        except GatewayException as e:
            # Handle known gateway exceptions
            error_response = ErrorResponse(
                code=e.code,
                message=e.message,
                request_id=get_request_id(),
                path=request.url.path,
                details=e.details
            )
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
        except Exception as e:
            # Log unexpected exceptions
            logger = logging.getLogger(__name__)
            logger.exception(f"Unexpected error: {e}")

            error_response = ErrorResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                request_id=get_request_id(),
                path=request.url.path,
                details={"error_type": type(e).__name__}
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )
