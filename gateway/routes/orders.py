"""
Order routes module for the API Gateway.

This module handles all order-related proxy requests to the backend service,
including CRUD operations (Create, Read, Update, Delete) and status updates.
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
router = APIRouter(prefix="/orders", tags=["orders"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="orders", filename="logs/api_gateway.log")
logger = create_logger(logger_name="orders")

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
    tags=["orders"],
    summary="List all orders",
    description="Proxies a GET request to retrieve all orders from the backend service with optional filtering."
)
@router.get(
    "/",
    tags=["orders"],
    summary="List all orders",
    description="Proxies a GET request to retrieve all orders from the backend service with optional filtering."
)
async def list_orders(
    request: Request,
    status_filter: str = Query(None, description="Filter by order status (new, picking, packing, shipped, cancelled)"),
    priority: int = Query(None, ge=1, le=5, description="Filter by priority level"),
    customer_name: str = Query(None, description="Filter by customer name"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return")
) -> Response:
    """
    List all orders with optional filtering and pagination.
    
    Proxies to Backend GET /orders or GET /orders/
    
    Retrieves orders from the backend with support for:
    - Filtering by order status (new, picking, packing, shipped, cancelled)
    - Filtering by priority level (1-5, where 1 is highest)
    - Filtering by customer name
    - Pagination via skip/limit
    
    Args:
        request: The incoming FastAPI Request.
        status_filter: Optional filter by order status.
        priority: Optional filter by priority level (1-5).
        customer_name: Optional filter by customer name.
        skip: Number of orders to skip (pagination).
        limit: Maximum number of orders to return.
    
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    
    Example:
        >>> curl "http://localhost:8080/api/v1/orders?status_filter=picking&priority=1"
    """
    try:
        # Build query parameters
        query_params = []
        if status_filter:
            query_params.append(f"status={status_filter}")
        if priority is not None:
            query_params.append(f"priority={priority}")
        if customer_name:
            query_params.append(f"customer_name={customer_name}")
        if skip:
            query_params.append(f"skip={skip}")
        if limit:
            query_params.append(f"limit={limit}")
        
        query_string = f"?{'&'.join(query_params)}" if query_params else ""
        
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/orders{query_string}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved orders list")
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
    "/{order_id}",
    tags=["orders"],
    summary="Get order by ID",
    description="Proxies a GET request to retrieve a single order by ID from the backend service."
)
async def get_order_by_id(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Get a single order by its ID.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/orders/{order_id}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found")
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
    tags=["orders"],
    summary="Create a new order",
    description="Proxies a POST request to create a new order in the backend service."
)
@router.post(
    "/",
    tags=["orders"],
    summary="Create a new order",
    description="Proxies a POST request to create a new order in the backend service."
)
async def create_order(request: Request) -> Response:
    """
    Create a new order.

    Args:
        request: The incoming FastAPI Request containing order data in the body.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint="/orders"
        )
        
        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"Successfully created new order")
            return Response(
                status_code=status.HTTP_201_CREATED,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning(f"Bad request when creating order")
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
    "/{order_id}",
    tags=["orders"],
    summary="Update an order",
    description="Proxies a PUT request to update an existing order in the backend service."
)
async def update_order(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Update an existing order.

    Args:
        request: The incoming FastAPI Request containing updated order data.
        order_id: The unique identifier of the order to update.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="put",
            endpoint=f"/orders/{order_id}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.info(f"Successfully updated order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning(f"Bad request when updating order {order_id}")
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


@router.patch(
    "/{order_id}/status",
    tags=["orders"],
    summary="Update order status",
    description="Proxies a PATCH request to update the status of an order."
)
async def update_order_status(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Update the status of an order.

    Args:
        request: The incoming FastAPI Request containing new status data.
        order_id: The unique identifier of the order.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="patch",
            endpoint=f"/orders/{order_id}/status"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.info(f"Successfully updated status for order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning(f"Bad request when updating status for order {order_id}")
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
    "/{order_id}",
    tags=["orders"],
    summary="Delete an order",
    description="Proxies a DELETE request to remove an order from the backend service."
)
async def delete_order(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Delete an order.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order to delete.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="delete",
            endpoint=f"/orders/{order_id}"
        )
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.info(f"Successfully deleted order {order_id}")
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found")
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


@router.get(
    "/{order_id}/lines",
    tags=["orders"],
    summary="Get order lines",
    description="Proxies a GET request to retrieve all order lines for a specific order."
)
async def get_order_lines(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Get all order lines for a specific order.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/orders/{order_id}/lines"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved order lines for order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found")
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


@router.patch(
    "/{order_id}/lines/{order_line_id}",
    tags=["orders"],
    summary="Update order line picked quantity",
    description="Proxies a PATCH request to update the picked quantity of a specific order line."
)
async def update_order_line_picked(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order"),
    order_line_id: int = Path(..., description="The unique identifier of the order line"),
) -> Response:
    """
    Update the quantity_picked for a specific order line.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order.
        order_line_id: The unique identifier of the order line.

    Returns:
        Response: A FastAPI Response with the updated order line.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="patch",
            endpoint=f"/orders/{order_id}/lines/{order_line_id}"
        )

        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully updated order line {order_line_id} for order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} or line {order_line_id} not found")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content,
                media_type="application/json"
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content,
                media_type="application/json"
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
    "/{order_id}/pallet-instructions",
    tags=["orders"],
    summary="Get pallet instructions for an order",
    description="Proxies a GET request to retrieve the generated pallet instructions JSON for a specific order."
)
async def get_pallet_instructions(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Retrieve pallet instructions for a specific order.

    This endpoint proxies the request to the backend service to fetch
    the most recent pallet instructions file generated by the packing algorithm.
    The response contains pallet configuration data for 3D visualization.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order.

    Returns:
        Response: A FastAPI Response with the pallet instructions JSON.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/orders/{order_id}/pallet-instructions"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved pallet instructions for order {order_id}")
            return Response(
                status_code=status.HTTP_200_OK,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Pallet instructions not found for order {order_id}")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content,
                media_type="application/json"
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content,
                media_type="application/json"
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error while fetching pallet instructions: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error while fetching pallet instructions: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )


@router.post(
    "/{order_id}/trigger-packing",
    tags=["orders"],
    summary="Trigger packing algorithm for an order",
    description="Proxies a POST request to manually trigger the packing algorithm for a specific order."
)
async def trigger_packing(
    request: Request,
    order_id: int = Path(..., description="The unique identifier of the order")
) -> Response:
    """
    Manually trigger the packing algorithm for a specific order.

    This endpoint queues the order for background processing.
    The packing algorithm will generate pallet instructions asynchronously.

    Args:
        request: The incoming FastAPI Request.
        order_id: The unique identifier of the order.

    Returns:
        Response: A FastAPI Response with status 202 (Accepted) if queued successfully.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint=f"/orders/{order_id}/trigger-packing"
        )
        
        if response.status_code == status.HTTP_202_ACCEPTED:
            logger.info(f"Successfully queued order {order_id} for packing")
            return Response(
                status_code=status.HTTP_202_ACCEPTED,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logger.warning(f"Order {order_id} not found for packing trigger")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.content,
                media_type="application/json"
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            logger.warning(f"Order {order_id} cannot be packed (invalid status)")
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=response.content,
                media_type="application/json"
            )
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return Response(
                status_code=response.status_code,
                content=response.content,
                media_type="application/json"
            )
    except httpx.HTTPStatusError as e:
        logger.critical(f"HTTP error while triggering packing: {e}")
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error while triggering packing: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e)
        )
