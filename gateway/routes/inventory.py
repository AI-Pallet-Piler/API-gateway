"""
Inventory routes module for the API Gateway.

This module handles all inventory-related proxy requests to the backend service,
including CRUD operations (Create, Read, Update, Delete).
"""

import httpx
from typing import Dict, Any
from fastapi import APIRouter, Response, Request, status, Query
from fastapi.params import Path
from fastapi.responses import JSONResponse

from gateway import config
from gateway.loggers import setup_logging, create_logger
from gateway.middlewares.request_id import get_request_id


# Create APIRouter instance with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/inventory", tags=["inventory"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="inventory", filename="logs/api_gateway.log")
logger = create_logger(logger_name="inventory")

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
    "",
    tags=["inventory"],
    summary="List all inventory",
    description="Proxies a GET request to retrieve all inventory from the backend service with optional filtering."
)
@router.get(
    "/",
    tags=["inventory"],
    summary="List all inventory",
    description="Proxies a GET request to retrieve all inventory from the backend service with optional filtering."
)
async def list_inventory(
    request: Request,
    product_id: int = Query(None, description="Filter by product ID"),
    location_id: int = Query(None, description="Filter by location ID"),
    sku: str = Query(None, description="Filter by product SKU"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return")
) -> Response:
    """
    List all inventory with optional filtering and pagination.

    Args:
        request: The incoming FastAPI Request.
        product_id: Optional filter by product ID.
        location_id: Optional filter by location ID.
        sku: Optional filter by product SKU.
        skip: Number of items to skip (pagination).
        limit: Maximum number of items to return.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        # Build query parameters
        query_params = []
        if product_id is not None:
            query_params.append(f"product_id={product_id}")
        if location_id is not None:
            query_params.append(f"location_id={location_id}")
        if sku:
            query_params.append(f"sku={sku}")
        if skip:
            query_params.append(f"skip={skip}")
        if limit:
            query_params.append(f"limit={limit}")
        
        query_string = f"?{'&'.join(query_params)}" if query_params else ""
        
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/inventory{query_string}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved inventory list")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )


@router.get(
    "/{inventory_id}",
    tags=["inventory"],
    summary="Get inventory by ID",
    description="Proxies a GET request to retrieve a single inventory record by ID from the backend service."
)
async def get_inventory_by_id(
    request: Request,
    inventory_id: int = Path(..., description="The unique identifier of the inventory record")
) -> Response:
    """
    Get a single inventory record by its ID.

    Args:
        request: The incoming FastAPI Request.
        inventory_id: The unique identifier of the inventory record.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/inventory/{inventory_id}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved inventory {inventory_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Inventory {inventory_id} not found")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )


@router.post(
    "",
    tags=["inventory"],
    summary="Create new inventory record",
    description="Proxies a POST request to create a new inventory record in the backend service."
)
@router.post(
    "/",
    tags=["inventory"],
    summary="Create new inventory record",
    description="Proxies a POST request to create a new inventory record in the backend service."
)
async def create_inventory(
    request: Request
) -> Response:
    """
    Create a new inventory record.

    Args:
        request: The incoming FastAPI Request containing inventory data.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint="/inventory"
        )
        
        if response.status_code == status.HTTP_201_CREATED:
            logger.debug("Successfully created inventory record")
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning("Bad request when creating inventory")
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=response.content
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )


@router.put(
    "/{inventory_id}",
    tags=["inventory"],
    summary="Update inventory by ID",
    description="Proxies a PUT request to update an inventory record by ID in the backend service."
)
async def update_inventory(
    request: Request,
    inventory_id: int = Path(..., description="The unique identifier of the inventory record")
) -> Response:
    """
    Update an inventory record by its ID.

    Args:
        request: The incoming FastAPI Request containing updated inventory data.
        inventory_id: The unique identifier of the inventory record to update.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="put",
            endpoint=f"/inventory/{inventory_id}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully updated inventory {inventory_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Inventory {inventory_id} not found for update")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning("Bad request when updating inventory")
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=response.content
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )


@router.delete(
    "/{inventory_id}",
    tags=["inventory"],
    summary="Delete inventory by ID",
    description="Proxies a DELETE request to delete an inventory record by ID in the backend service."
)
async def delete_inventory(
    request: Request,
    inventory_id: int = Path(..., description="The unique identifier of the inventory record")
) -> Response:
    """
    Delete an inventory record by its ID.

    Args:
        request: The incoming FastAPI Request.
        inventory_id: The unique identifier of the inventory record to delete.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="delete",
            endpoint=f"/inventory/{inventory_id}"
        )
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.debug(f"Successfully deleted inventory {inventory_id}")
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Inventory {inventory_id} not found for deletion")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )
