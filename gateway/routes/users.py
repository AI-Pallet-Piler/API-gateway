"""
User routes module for the API Gateway.

This module handles all user-related proxy requests to the backend service,
including CRUD operations (Create, Read, Update, Delete).
"""

import httpx
from typing import Optional, Dict, Any
from fastapi import APIRouter, Response, Request, status
from fastapi.params import Path
from fastapi.responses import JSONResponse

from gateway import config
from gateway.loggers import setup_logging, create_logger
from gateway.middlewares.request_id import get_request_id


# Create APIRouter instance with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/users", tags=["users"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="users", filename="logs/api_gateway.log")
logger = create_logger(logger_name="users")

# Create async HTTP client for proxying requests
client = httpx.AsyncClient(timeout=30.0)


async def proxy_request(
    request: Request,
    method: str,
    endpoint: str = "/"
) -> httpx.Response:
    """
    Proxy an incoming request to the backend service.

    This function forwards the incoming request to the configured backend
    service, preserving the method, body, and headers while adding a
    request ID for tracing purposes.

    Args:
        request: The incoming FastAPI Request object.
        method: The HTTP method to use when proxying (e.g., "get", "post").
        endpoint: The backend endpoint path to proxy to. Defaults to "/".

    Returns:
        httpx.Response: The response from the backend service.

    Raises:
        httpx.HTTPStatusError: If the backend returns an error status code.
        httpx.RequestError: If there's a network error communicating with the backend.
    """
    request_id: str = get_request_id()
    headers: Dict[str, str] = dict(request.headers)
    headers["X-Request-ID"] = request_id  # Propagate to backend

    body: bytes = await request.body()
    full_url: str = settings.url_backend + endpoint
    logger.debug(f"Proxy request URL: {full_url}")
    response: httpx.Response = await client.request(
        method,
        full_url,
        content=body,
        headers=headers
    )
    return response

@router.get(
    "/{user_id}",
    tags=["users"],
    summary="Get user by ID",
    description="Proxies a GET request to completely get a user by ID in the backend service."
)
async def replace_user_by_id(
    request: Request,
    user_id: str = Path(..., description="The unique identifier of the user")
) -> Response:
    """
    Replace a user by their ID using PUT method (full update).
    Args:
        request: The incoming FastAPI Request containing user data.
        user_id: The unique identifier of the user to replace.
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/{user_id}"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )

@router.put(
    "/{user_id}",
    tags=["users"],
    summary="replace user by ID",
    description="Proxies a put request to completely replace a user by ID in the backend service."
)
async def replace_user_by_id(
    request: Request,
    user_id: str = Path(..., description="The unique identifier of the user")
) -> Response:
    """
    Replace a user by their ID using PUT method (full update).
    Args:
        request: The incoming FastAPI Request containing user data.
        user_id: The unique identifier of the user to replace.
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/{user_id}"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )

@router.patch(
    "/{user_id}",
    tags=["users"],
    summary="patch user by ID",
    description="Proxies a patch request to completely get a update by ID in the backend service."
)
async def replace_user_by_id(
    request: Request,
    user_id: str = Path(..., description="The unique identifier of the user")
) -> Response:
    """
    Replace a user by their ID using PUT method (full update).
    Args:
        request: The incoming FastAPI Request containing user data.
        user_id: The unique identifier of the user to replace.
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/{user_id}"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )

@router.delete(
    "/{user_id}",
    tags=["users"],
    summary="delete user by ID",
    description="Proxies a delete request to completely delete a user by ID in the backend service."
)
async def replace_user_by_id(
    request: Request,
    user_id: str = Path(..., description="The unique identifier of the user")
) -> Response:
    """
    Replace a user by their ID using PUT method (full update).
    Args:
        request: The incoming FastAPI Request containing user data.
        user_id: The unique identifier of the user to replace.
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/{user_id}"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )

@router.put(
    "/create",
    tags=["users"],
    summary="Create a new user via PUT",
    description="Proxies a PUT request to create a new user in the backend service."
)
async def create_user(request: Request) -> Response:
    """
    Create a new user using PUT method.

    Args:
        request: The incoming FastAPI Request containing user data.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="put",
            endpoint="/create"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )

@router.get(
    "/",
    tags=["users"],
    summary="Get a user via GET",
    description="Proxies a GET request to retrieve a user from the backend service."
)
async def get_user(request: Request) -> Response:
    """
    Get a user using GET method.

    Args:
        request: The incoming FastAPI Request.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint="/get"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.warning(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )


@router.post(
    "/create",
    tags=["users"],
    summary="Create a new user via POST",
    description="Proxies a POST request to create a new user in the backend service."
)
async def create_user_post(request: Request) -> Response:
    """
    Create a new user using POST method.

    This is an alternative endpoint to create_user that uses POST instead of PUT.

    Args:
        request: The incoming FastAPI Request containing user data.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint="/create"
        )
        if response.status_code == status.HTTP_200_OK:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content
            )
        elif response.status_code == status.HTTP_201_CREATED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content
            )
        elif response.status_code == status.HTTP_202_ACCEPTED:
            logger.debug(response)
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content
            )
        else:
            logger.warning(response.status_code)
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(e)
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
