"""
Metrics routes module for the API Gateway.

This module provides Prometheus metrics endpoints for monitoring
request rates, durations, errors, and upstream service metrics.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    to_float
)
from datetime import datetime


# Create router for metrics endpoints
router = APIRouter(tags=["metrics"])

# Create a custom registry (good for isolation)
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

REQUEST_DURATION = Histogram(
    'gateway_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=registry
)

# Upstream service metrics
UPSTREAM_REQUEST_COUNT = Counter(
    'gateway_upstream_requests_total',
    'Total number of upstream requests',
    ['upstream', 'method', 'status_code'],
    registry=registry
)

UPSTREAM_REQUEST_DURATION = Histogram(
    'gateway_upstream_request_duration_seconds',
    'Upstream request duration in seconds',
    ['upstream', 'method'],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    registry=registry
)

# Error tracking
ERROR_COUNT = Counter(
    'gateway_errors_total',
    'Total number of errors',
    ['type', 'endpoint'],
    registry=registry
)

# Active connections
ACTIVE_CONNECTIONS = Gauge(
    'gateway_active_connections',
    'Number of active connections',
    registry=registry
)


class MetricsMiddleware:
    """
    Helper class for recording request metrics.

    This class provides static methods to record various metrics
    including request counts, durations, and errors.
    """

    @staticmethod
    def record_request(
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ) -> None:
        """
        Record metrics for an incoming request.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            endpoint: The request endpoint path.
            status_code: HTTP status code of the response.
            duration: Request duration in seconds.

        Example:
            >>> MetricsMiddleware.record_request(
            ...     method="GET",
            ...     endpoint="/api/v1/users",
            ...     status_code=200,
            ...     duration=0.05
            ... )
        """
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()

        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Record error if status code indicates error
        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()


@router.get(
    "/metrics",
    summary="Prometheus metrics endpoint",
    description="Export metrics in Prometheus format for scraping by Prometheus."
)
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in the Prometheus text format for collection
    by Prometheus servers.

    Returns:
        Response: A Response object with metrics content in Prometheus format.

    Example:
        >>> response = await client.get("/metrics")
        >>> print(response.text[:200])
        # gateway_requests_total{method="GET",endpoint="/health",status_code="200"} 123.0
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get(
    "/metrics/json",
    summary="JSON metrics endpoint",
    description="Export metrics in JSON format for custom dashboards and monitoring."
)
async def metrics_json() -> Dict[str, Any]:
    """
    JSON metrics endpoint.

    Returns detailed metrics in JSON format suitable for custom
    dashboards and external monitoring systems.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - timestamp: ISO format timestamp
            - requests: Request counts by endpoint and status
            - errors: Error counts by type
            - active_connections: Current number of active connections

    Example:
        >>> response = await client.get("/metrics/json")
        >>> response.json()
        {
            "timestamp": "2024-01-15T10:30:00.000Z",
            "requests": {"total": 1500, "by_endpoint": {...}},
            "errors": {"total": 5, "by_type": {...}},
            "active_connections": 10
        }
    """
    metrics_data: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "requests": {
            "total": to_float(REQUEST_COUNT),
            "by_endpoint": {},
        },
        "errors": {
            "total": to_float(ERROR_COUNT),
            "by_type": {},
        },
        "active_connections": to_float(ACTIVE_CONNECTIONS),
    }

    # Collect endpoint-specific metrics
    for sample in REQUEST_COUNT.collect()[0].samples:
        endpoint = sample.labels.get("endpoint", "unknown")
        if endpoint not in metrics_data["requests"]["by_endpoint"]:
            metrics_data["requests"]["by_endpoint"][endpoint] = {
                "total": 0,
                "by_status": {}
            }
        metrics_data["requests"]["by_endpoint"][endpoint]["total"] = sample.value
        status = sample.labels.get("status_code", "unknown")
        metrics_data["requests"]["by_endpoint"][endpoint]["by_status"][status] = sample.value

    return metrics_data
