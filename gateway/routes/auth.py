"""
Auth routes module for the API Gateway.

This module handles authentication-related proxy requests to the backend service.
"""

import httpx
from fastapi import APIRouter, Response, Request, status
from fastapi.params import Path

from gateway import config
from gateway.loggers import setup_logging, create_logger
from gateway.middlewares.request_id import get_request_id


# Create APIRouter instance with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="auth", filename="logs/api_gateway.log")
logger = create_logger(logger_name="auth")

# Create async HTTP client for proxying requests
client = httpx.AsyncClient(timeout=30.0)


async def proxy_request(
    request: Request,
    method: str,
    endpoint: str = "/"
) -> httpx.Response:
    """
    Proxy a request to the backend service.
    """
    request_id: str = get_request_id()
    headers: dict = dict(request.headers)
    headers["X-Request-ID"] = request_id
    headers.pop("host", None)
    
    body = await request.body()
    # Auth endpoints are at /api/auth, not /api/v1/auth
    base_url = settings.url_backend.replace("/api/v1", "")
    url = f"{base_url}{endpoint}"
    
    logger.debug(f"Proxy auth request to: {url}")
    
    response = await client.request(
        method=method,
        url=url,
        headers=headers,
        content=body
    )
    
    return response


@router.post(
    "/login",
    tags=["auth"],
    summary="Login user",
    description="Authenticates a user with email and password."
)
async def login(request: Request) -> Response:
    """
    Authenticate a user with email and password.
    Proxies to the backend's /api/auth/validate endpoint.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint="/api/auth/validate"
        )
        
        logger.debug(f"Login response status: {response.status_code}")
        
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json"
        )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error during login: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Error during login: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
