"""
Health check routes module for the API Gateway.

This module provides various health check endpoints for monitoring
the gateway and its upstream services, including Kubernetes readiness
and liveness probes.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime


# Create router for health endpoints
router = APIRouter(tags=["health"])

# Configuration for upstream services to check during readiness
UPSTREAM_SERVICES: Dict[str, Dict[str, Any]] = {
    "users_service": {"url": "http://users-service:8000/health", "timeout": 5.0},
    "auth_service": {"url": "http://auth-service:8001/health", "timeout": 5.0},
}

# In-memory health state (could be replaced with Redis for distributed systems)
health_status: Dict[str, Any] = {
    "status": "healthy",
    "timestamp": None,
    "components": {}
}


@router.get(
    "/",
    summary="Basic health check",
    description="Returns 200 if the gateway is responding. Used for basic health monitoring."
)
async def basic_health() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        Dict[str, str]: A dictionary containing status and timestamp.

    Example:
        >>> response = await client.get("/health/")
        >>> response.json()
        {"status": "ok", "timestamp": "2024-01-15T10:30:00.000Z"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/live",
    summary="Kubernetes liveness probe",
    description="Kubernetes liveness probe - should respond quickly without checking upstream services."
)
async def liveness() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.

    This endpoint should be lightweight and only check if the application
    process is running. It does not check upstream dependencies.

    Returns:
        Dict[str, str]: A simple status response.

    Example:
        >>> response = await client.get("/health/live")
        >>> response.json()
        {"status": "alive"}
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Kubernetes readiness probe",
    description="Kubernetes readiness probe - checks if gateway can accept traffic by verifying upstream services."
)
async def readiness() -> JSONResponse:
    """
    Kubernetes readiness probe endpoint.

    This endpoint checks if the gateway can accept traffic by verifying
    that all upstream services are reachable and healthy. Returns 503
    if any upstream service is unhealthy.

    Returns:
        JSONResponse: A response containing overall status and component health.
            - 200: All services healthy
            - 503: One or more services unhealthy (degraded status)

    Example:
        >>> response = await client.get("/health/ready")
        >>> response.status_code
        200
        >>> response.json()
        {"status": "healthy", "components": {"users_service": {"status": "healthy"}}}
    """
    # Update the timestamp for this health check
    health_status["timestamp"] = datetime.utcnow().isoformat()

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for name, config in UPSTREAM_SERVICES.items():
            tasks.append(
                check_service_health(
                    client,
                    name,
                    config["url"],
                    config["timeout"]
                )
            )

        # Wait for all health checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Aggregate results
    all_healthy = True
    for i, (name, _) in enumerate(UPSTREAM_SERVICES.items()):
        result = results[i]
        if isinstance(result, Exception):
            health_status["components"][name] = {
                "status": "unhealthy",
                "error": str(result)
            }
            all_healthy = False
        else:
            health_status["components"][name] = {"status": "healthy"}

    health_status["status"] = "healthy" if all_healthy else "degraded"

    if not all_healthy:
        return JSONResponse(
            content={
                "status": "degraded",
                "components": health_status["components"]
            },
            status_code=503
        )

    return {
        "status": "healthy",
        "components": health_status["components"]
    }


async def check_service_health(
    client: httpx.AsyncClient,
    name: str,
    url: str,
    timeout: float
) -> bool:
    """
    Check individual service health.

    Args:
        client: The httpx AsyncClient to use for the request.
        name: The name of the service (for logging/tracking).
        url: The health check URL of the service.
        timeout: Request timeout in seconds.

    Returns:
        bool: True if service is healthy (returns 200), False otherwise.
        Exception: Returns the exception object if request fails.
    """
    try:
        response = await client.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return e


async def periodic_health_check() -> None:
    """
    Periodic background task to update health status.

    This function runs in the background and periodically checks
    the health of upstream services, updating the health_status dict.
    It sleeps for 30 seconds between checks.

    Warning:
        This is an infinite loop intended to run as a background task.

    Example:
        >>> health_check_task = asyncio.create_task(periodic_health_check())
    """
    while True:
        # Call readiness to update the health_status dict
        await readiness()
        # Wait before next check
        await asyncio.sleep(30)
