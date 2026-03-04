"""
Authentication routes module for the API Gateway.

This module handles authentication-related proxy requests to the Security API service,
including login (email/password and badge), token refresh, logout, and token validation.
"""

import httpx
import os
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
    
    This function forwards authentication requests to the configured Security API
    service, preserving the HTTP method, request body, and headers while adding
    a request ID for distributed tracing.
    
    Args:
        request: The incoming FastAPI Request object.
        method: The HTTP method to use when proxying (e.g., "get", "post").
        endpoint: The security-api endpoint path to proxy to. Defaults to "/".
    
    Returns:
        httpx.Response: The response from the security-api service.
    
    Raises:
        httpx.HTTPStatusError: If the security API returns an error status code.
        httpx.RequestError: If there's a network error communicating with the security API.
    
    Example:
        >>> response = await proxy_request(request, "POST", "/login")
    """
    # Get the security API URL from config or environment
    security_api_url = settings.security_api_url
    logger.info(f"Using SECURITY_API_URL: {security_api_url}")
    
    # Build the full URL
    url = f"{security_api_url}/auth/v1{endpoint}"
    logger.info(f"Proxying {method} request to: {url}")
    
    # Get request body if present
    body = None
    if method.lower() in ["post", "put", "patch"]:
        try:
            body = await request.json()
            logger.debug(f"Request body: {body}")
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")
            body = None
    
    # Get request headers (only content-type and user headers, not host)
    headers = {}
    if "content-type" in request.headers:
        headers["content-type"] = request.headers["content-type"]
    
    # Get request ID for tracing
    request_id = get_request_id()
    if request_id:
        headers["X-Request-Id"] = request_id
    
    logger.debug(f"Request headers: {headers}")
    
    # Make the proxied request
    try:
        logger.info(f"Making request: {method} {url}")
        response = await client.request(
            method=method,
            url=url,
            json=body,
            headers=headers,
        )
        logger.info(f"Response status: {response.status_code}")
        return response
    except httpx.RequestError as e:
        logger.error(f"HTTP error proxying request to security-api: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error proxying request: {e}", exc_info=True)
        raise


@router.post("/login")
async def login(request: Request) -> Response:
    """
    Email/password login endpoint.
    
    Proxies to Security API POST /auth/v1/login
    
    Authenticates a user using their email and password credentials.
    Returns access and refresh tokens upon successful authentication.
    
    Request Body:
        email (str): User's email address
        password (str): User's password
    
    Returns:
        Response: Token response containing access_token, refresh_token, and token_type
    
    Raises:
        HTTP 401: Invalid email or password
        HTTP 500: Authentication service error
    
    Example:
        >>> curl -X POST http://localhost:8080/api/v1/auth/login \\
        >>>   -H "Content-Type: application/json" \\
        >>>   -d '{"email": "user@example.com", "password": "secret"}'
    """
    try:
        logger.info("Login request received")
        response = await proxy_request(request, "POST", "/login")
        
        # Return response with same status code
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Login endpoint error: {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error", "error": str(e)}
        )


@router.post("/login-badge")
async def login_badge(request: Request) -> Response:
    """
    Badge-based login endpoint for warehouse pickers.
    
    Proxies to Security API POST /auth/v1/login-badge
    
    Authenticates a picker using their badge ID instead of email/password.
    Commonly used in warehouse environments for quick authentication.
    
    Request Body:
        badge_id (str): Picker badge identifier
    
    Returns:
        Response: Token response containing access_token, refresh_token, and token_type
    
    Raises:
        HTTP 401: Invalid badge ID
        HTTP 500: Authentication service error
    
    Example:
        >>> curl -X POST http://localhost:8080/api/v1/auth/login-badge \\
        >>>   -H "Content-Type: application/json" \\
        >>>   -d '{"badge_id": "BADGE12345"}'
    """
    try:
        logger.info("Badge login request received")
        response = await proxy_request(request, "POST", "/login-badge")
        
        # Return response with same status code
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Badge login endpoint error: {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error", "error": str(e)}
        )


@router.post("/refresh")
async def refresh(request: Request) -> Response:
    """
    Token refresh endpoint.
    
    Proxies to Security API POST /auth/v1/refresh
    
    Refreshes an expired or expiring access token using a valid refresh token.
    
    Request Body:
        refresh_token (str): The refresh token from previous login
    
    Returns:
        Response: New token response with fresh access_token and refresh_token
    
    Raises:
        HTTP 401: Invalid or expired refresh token
        HTTP 500: Authentication service error
    
    Example:
        >>> curl -X POST http://localhost:8080/api/v1/auth/refresh \\
        >>>   -H "Content-Type: application/json" \\
        >>>   -d '{"refresh_token": "eyJhbGc..."}'
    """
    try:
        logger.info("Token refresh request received")
        response = await proxy_request(request, "POST", "/refresh")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error", "error": str(e)}
        )


@router.post("/logout")
async def logout(request: Request) -> Response:
    """
    Logout endpoint.
    
    Proxies to Security API POST /auth/v1/logout
    
    Invalidates the current session and tokens. Should be called when
    the user wants to terminate their session.
    
    Request Body:
        access_token (str): The current access token (optional)
    
    Returns:
        Response: Confirmation of logout success
    
    Raises:
        HTTP 500: Authentication service error
    
    Example:
        >>> curl -X POST http://localhost:8080/api/v1/auth/logout \\
        >>>   -H "Authorization: Bearer <access_token>"
    """
    try:
        logger.info("Logout request received")
        response = await proxy_request(request, "POST", "/logout")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Logout endpoint error: {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error", "error": str(e)}
        )


@router.post("/validate")
async def validate(request: Request) -> Response:
    """
    Token validation endpoint.
    
    Proxies to Security API POST /auth/v1/validate
    
    Validates an access token and returns user information if valid.
    Used by backend services to verify authenticated requests.
    
    Request Body:
        email (str): User's email address
        password (str): User's password to validate
    
    Returns:
        Response: User information including id, email, role, and hashed_password
    
    Raises:
        HTTP 401: Invalid credentials
        HTTP 500: Authentication service error
    
    Example:
        >>> curl -X POST http://localhost:8080/api/v1/auth/validate \\
        >>>   -H "Content-Type: application/json" \\
        >>>   -d '{"email": "user@example.com", "password": "secret"}'
    """
    try:
        logger.info("Token validation request received")
        response = await proxy_request(request, "POST", "/validate")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Token validation endpoint error: {type(e).__name__}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Authentication service error", "error": str(e)}
        )
