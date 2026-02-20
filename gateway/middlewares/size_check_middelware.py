"""
Size check middleware module.

This middleware validates that incoming request bodies do not exceed
a configured maximum size limit to prevent resource exhaustion attacks.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Union


# Maximum allowed request body size in bytes (10MB)
MAX_SIZE: int = 10 * 1024 * 1024  # 10MB


class CheckSizeMiddelware(BaseHTTPMiddleware):
    """
    Middleware to check request body size against maximum allowed limit.

    This middleware intercepts incoming requests and checks the Content-Length
    header to ensure the request body does not exceed MAX_SIZE. Requests that
    exceed this limit will receive a 413 Payload Too Large response.

    Attributes:
        max_size: Maximum allowed body size in bytes. Defaults to 10MB.

    Example:
        >>> app.add_middleware(CheckSizeMiddelware)
    """

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Union[Response, HTTPException]:
        """
        Process the request and check body size.

        Args:
            request: The incoming FastAPI Request object.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The response from the next handler if size is valid.
            HTTPException: A 413 response if the body exceeds the size limit.

        Raises:
            HTTPException: When Content-Length exceeds MAX_SIZE.
        """
        content_length_header: str = request.headers.get("content-length", "0")
        content_length: int = int(content_length_header)

        if content_length > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Request body too large. Maximum size is 10MB."
            )

        return await call_next(request)
