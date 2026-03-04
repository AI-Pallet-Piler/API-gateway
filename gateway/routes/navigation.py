"""
Navigation routes module for the API Gateway.

This module handles all navigation-related proxy requests to the backend service,
including warehouse map retrieval, location lookups, and path-finding between locations.
"""

import httpx
from fastapi import APIRouter, Response, Request, status
from fastapi.params import Path

from gateway import config
from gateway.loggers import setup_logging, create_logger
from gateway.middlewares.request_id import get_request_id


# Create APIRouter instance with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/navigation", tags=["navigation"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="navigation", filename="logs/api_gateway.log")
logger = create_logger(logger_name="navigation")

# Create async HTTP client for proxying requests
client = httpx.AsyncClient(timeout=30.0)


async def proxy_request(
    request: Request,
    method: str,
    endpoint: str = "/"
) -> httpx.Response:
    """
    Proxy an incoming request to the backend service.

    Args:
        request: The incoming FastAPI Request object.
        method: The HTTP method to use when proxying.
        endpoint: The backend endpoint path to proxy to.

    Returns:
        httpx.Response: The response from the backend service.
    """
    request_id: str = get_request_id()
    headers: dict = dict(request.headers)
    headers["X-Request-ID"] = request_id

    body: bytes = await request.body()
    full_url: str = settings.url_backend + endpoint
    logger.debug(f"Proxy request URL: {full_url}")
    response: httpx.Response = await client.request(
        method,
        full_url,
        content=body,
        headers=headers,
    )
    return response


@router.get(
    "/map",
    tags=["navigation"],
    summary="Get warehouse map",
    description="Retrieve the full warehouse map including corridors, shelves, connections and connection points.",
)
async def get_warehouse_map(request: Request) -> Response:
    """Get the current warehouse map with all geometric components."""
    try:
        response = await proxy_request(request, "get", "/navigation/map")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.HTTPStatusError as exc:
        logger.critical(f"HTTP error fetching warehouse map: {exc}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=str(exc))
    except Exception as exc:
        logger.critical(f"Unexpected error fetching warehouse map: {exc}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc))


@router.get(
    "/locations",
    tags=["navigation"],
    summary="Get all locations",
    description="Retrieve all warehouse locations with shelf associations and coordinates.",
)
async def get_locations(request: Request) -> Response:
    """Get all warehouse locations."""
    try:
        response = await proxy_request(request, "get", "/navigation/locations")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.HTTPStatusError as exc:
        logger.critical(f"HTTP error fetching locations: {exc}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=str(exc))
    except Exception as exc:
        logger.critical(f"Unexpected error fetching locations: {exc}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc))


@router.get(
    "/path/code/{from_code}/{to_code}",
    tags=["navigation"],
    summary="Get path between location codes",
    description="Find the shortest navigation path between two locations identified by their codes (e.g. LOC-001).",
)
async def get_path_by_code(
    request: Request,
    from_code: str = Path(..., description="Source location code"),
    to_code: str = Path(..., description="Destination location code"),
) -> Response:
    """Get navigation path between two location codes."""
    try:
        response = await proxy_request(
            request, "get", f"/navigation/path/code/{from_code}/{to_code}"
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.HTTPStatusError as exc:
        logger.critical(f"HTTP error fetching path: {exc}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=str(exc))
    except Exception as exc:
        logger.critical(f"Unexpected error fetching path: {exc}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc))


@router.get(
    "/path/{from_shelf_id}/{to_shelf_id}",
    tags=["navigation"],
    summary="Get path between shelves",
    description="Find the shortest navigation path between two shelves by their IDs.",
)
async def get_path_by_shelf(
    request: Request,
    from_shelf_id: int = Path(..., description="Source shelf ID"),
    to_shelf_id: int = Path(..., description="Destination shelf ID"),
) -> Response:
    """Get navigation path between two shelf IDs."""
    try:
        response = await proxy_request(
            request, "get", f"/navigation/path/{from_shelf_id}/{to_shelf_id}"
        )
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.HTTPStatusError as exc:
        logger.critical(f"HTTP error fetching shelf path: {exc}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=str(exc))
    except Exception as exc:
        logger.critical(f"Unexpected error fetching shelf path: {exc}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc))


@router.post(
    "/generate-and-sync",
    tags=["navigation"],
    summary="Generate warehouse map and sync",
    description="Generate the warehouse map, sync locations with shelves, and compute all paths.",
)
async def generate_and_sync(request: Request) -> Response:
    """Generate warehouse map and sync locations."""
    try:
        response = await proxy_request(request, "post", "/navigation/generate-and-sync")
        return Response(
            status_code=response.status_code,
            content=response.content,
            media_type="application/json",
        )
    except httpx.HTTPStatusError as exc:
        logger.critical(f"HTTP error during generate-and-sync: {exc}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=str(exc))
    except Exception as exc:
        logger.critical(f"Unexpected error during generate-and-sync: {exc}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc))
