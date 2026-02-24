"""
Authentication routes module for the API Gateway.

This module handles authentication-related proxy requests to the Security API service,
including login (email/password and badge), token refresh, logout, and token validation.
"""

import httpx
from typing import Optional, Dict, Any
from fastapi import APIRouter, Response, Request, status
from fastapi.responses import JSONResponse

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
    Proxy an incoming request to the Security API service.

    Args:
        request: The incoming FastAPI Request object.
        method: The HTTP method to use when proxying (e.g., "get", "post").
        endpoint: The security-api endpoint path to proxy to. Defaults to "/".

    Returns:
        The response from the security-api service.
    """
    # Get the security API URL from config
    security_api_url = getattr(settings, "security_api_url", "http://localhost:8000")
    
    # Build the full URL
    url = f"{security_api_url}/auth/v1{endpoint}"
    
    # Get request body if present
    body = None
    if method.lower() in ["post", "put", "patch"]:
        try:
            body = await request.json()
        except:
            pass
    
    # Get request headers
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Get request ID for tracing
    request_id = get_request_id()
    if request_id:
        headers["X-Request-Id"] = request_id
    
    # Make the proxied request
    try:
        response = await client.request(
            method=method,
            url=url,
            json=body,
            headers=headers,
        )
        return response
    except httpx.RequestError as e:
        logger.error(f"Error proxying request to security-api: {e}")
        raise


@router.post("/login")
async def login(request: Request) -> Response:
    """
    Email/password login endpoint.
    Proxies to Security API /auth/v1/login
    """
    try:
        response = await proxy_request(request, "POST", "/login")
        
        # Return response with same status code
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error"}
        )


@router.post("/login-badge")
async def login_badge(request: Request) -> Response:
    """
    Badge-based login endpoint for pickers.
    Proxies to Security API /auth/v1/login-badge
    """
    try:
        response = await proxy_request(request, "POST", "/login-badge")
        
        # Return response with same status code
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Badge login error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error"}
        )


@router.post("/refresh")
async def refresh(request: Request) -> Response:
    """
    Token refresh endpoint.
    Proxies to Security API /auth/v1/refresh
    """
    try:
        response = await proxy_request(request, "POST", "/refresh")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error"}
        )


@router.post("/logout")
async def logout(request: Request) -> Response:
    """
    Logout endpoint.
    Proxies to Security API /auth/v1/logout
    """
    try:
        response = await proxy_request(request, "POST", "/logout")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error"}
        )


@router.post("/validate")
async def validate(request: Request) -> Response:
    """
    Token validation endpoint.
    Proxies to Security API /auth/v1/validate
    """
    try:
        response = await proxy_request(request, "POST", "/validate")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error"}
        )
