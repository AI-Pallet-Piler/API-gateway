"""
API Gateway package for the warehouse management system.

This package provides the main FastAPI application and its configuration,
acting as a reverse proxy that routes requests to various backend services
including user management, product catalog, inventory tracking, order processing,
navigation, and reporting.

The gateway provides:
    - Request routing and proxying to backend services
    - Authentication and authorization handling
    - Request/response logging and metrics collection
    - Health checks for Kubernetes probes
    - Rate limiting and size validation
    - Distributed tracing via request IDs

Main Components:
    - config: Application settings and configuration
    - main: FastAPI application initialization
    - loggers: Structured JSON logging setup
    - middlewares: Request processing middleware
    - routes: API route handlers for all services
    - other: Utilities including exceptions


Usage:
    Run the gateway as a standalone service:
    
    >>> python -m gateway.main
    
    Or use with uvicorn:
    
    >>> uvicorn gateway.main:app --host 0.0.0.0 --port 8080

Environment Variables:
    - URL_BACKEND: Base URL for the backend service
    - SECURITY_API_URL: Base URL for the security/auth service
    - GRACEFUL_SHUTDOWN_TIMEOUT: Timeout for graceful shutdown (default: 30s)

Example:
    Basic configuration via environment:
    
    >>> export URL_BACKEND=http://backend:8000
    >>> export SECURITY_API_URL=http://security-api:8000
    >>> python -m gateway.main
"""

__version__ = "0.1.0"
