"""
Report routes module for the API Gateway.

This module handles all report-related proxy requests to the backend service,
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
router = APIRouter(prefix="/reports", tags=["reports"])

# Initialize settings from configuration
settings = config.Settings()

# Set up logging for this module
setup_logging(logger_name="reports", filename="logs/api_gateway.log")
logger = create_logger(logger_name="reports")

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
    tags=["reports"],
    summary="List all reports",
    description="Proxies a GET request to retrieve all reports from the backend service with optional filtering."
)
@router.get(
    "/",
    tags=["reports"],
    summary="List all reports",
    description="Proxies a GET request to retrieve all reports from the backend service with optional filtering."
)
async def list_reports(
    request: Request,
    order_id: int = Query(None, description="Filter by order ID"),
    issue_type: str = Query(None, description="Filter by issue type (damage, missing, blocked, other)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return")
) -> Response:
    """
    List all reports with optional filtering and pagination.
    
    Proxies to Backend GET /reports or GET /reports/
    
    Retrieves reports from the backend with support for:
    - Filtering by order ID
    - Filtering by issue type (damage, missing, blocked, other)
    - Pagination via skip/limit
    
    Args:
        request: The incoming FastAPI Request.
        order_id: Optional filter by order ID.
        issue_type: Optional filter by issue type.
        skip: Number of reports to skip (pagination).
        limit: Maximum number of reports to return.
    
    Returns:
        Response: A FastAPI Response with the backend's response content and status code.
    
    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    
    Example:
        >>> curl "http://localhost:8080/api/v1/reports?issue_type=damage&limit=20"


    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        # Build query parameters
        query_params = []
        if order_id is not None:
            query_params.append(f"order_id={order_id}")
        if issue_type:
            query_params.append(f"issue_type={issue_type}")
        if skip:
            query_params.append(f"skip={skip}")
        if limit:
            query_params.append(f"limit={limit}")
        
        query_string = f"?{'&'.join(query_params)}" if query_params else ""
        
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/reports{query_string}"
        )
        
        if response.status_code == status.HTTP_200_OK:
            logger.debug(f"Successfully retrieved reports list")
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
    "/{report_id}",
    tags=["reports"],
    summary="Get a specific report",
    description="Proxies a GET request to retrieve a specific report by ID from the backend service."
)
async def get_report(
    request: Request,
    report_id: int = Path(..., ge=1, description="The report ID")
) -> Response:
    """
    Get a specific report by ID.

    Args:
        request: The incoming FastAPI Request.
        report_id: The ID of the report to retrieve.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="get",
            endpoint=f"/reports/{report_id}"
        )
        
        if response.status_code in (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND):
            return Response(
                status_code=response.status_code,
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


@router.post(
    "",
    tags=["reports"],
    summary="Create a new report",
    description="Proxies a POST request to create a new report in the backend service."
)
@router.post(
    "/",
    tags=["reports"],
    summary="Create a new report",
    description="Proxies a POST request to create a new report in the backend service."
)
async def create_report(request: Request) -> Response:
    """
    Create a new report.

    Args:
        request: The incoming FastAPI Request with report data in the body.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="post",
            endpoint="/reports"
        )
        
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND):
            return Response(
                status_code=response.status_code,
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


@router.put(
    "/{report_id}",
    tags=["reports"],
    summary="Update a report",
    description="Proxies a PUT request to update an existing report in the backend service."
)
async def update_report(
    request: Request,
    report_id: int = Path(..., ge=1, description="The report ID")
) -> Response:
    """
    Update an existing report.

    Args:
        request: The incoming FastAPI Request with updated report data in the body.
        report_id: The ID of the report to update.

    Returns:
        Response: A FastAPI Response with the backend's response content and status code.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="put",
            endpoint=f"/reports/{report_id}"
        )
        
        if response.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND):
            return Response(
                status_code=response.status_code,
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


@router.delete(
    "/{report_id}",
    tags=["reports"],
    summary="Delete a report",
    description="Proxies a DELETE request to delete a report from the backend service."
)
async def delete_report(
    request: Request,
    report_id: int = Path(..., ge=1, description="The report ID")
) -> Response:
    """
    Delete a report by ID.

    Args:
        request: The incoming FastAPI Request.
        report_id: The ID of the report to delete.

    Returns:
        Response: A FastAPI Response with status 204 No Content on success.

    Raises:
        httpx.HTTPStatusError: If the backend service returns an error.
    """
    try:
        response: httpx.Response = await proxy_request(
            request=request,
            method="delete",
            endpoint=f"/reports/{report_id}"
        )
        
        if response.status_code in (status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND):
            return Response(
                status_code=response.status_code,
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
