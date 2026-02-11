"""
API Gateway main application module.

This module initializes the FastAPI application, configures middleware,
sets up routing, and handles graceful shutdown of the gateway.
"""

import asyncio
import os
import signal
from contextlib import asynccontextmanager
from typing import Optional, Any

import httpx
import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gateway.loggers import setup_logging, create_logger
from gateway.middlewares import (
    log_middelware,
    size_check_middelware,
    exception_handler
)
from gateway.routes import users, products, inventory, health, metrics, extras

# Global HTTP client reference
http_client: Optional[httpx.AsyncClient] = None

# Graceful shutdown configuration from environment variables
GRACEFUL_SHUTDOWN_TIMEOUT: int = int(os.getenv("GRACEFUL_SHUTDOWN_TIMEOUT", "30"))
MAX_CONNECTIONS_DRAIN_TIME: int = int(os.getenv("MAX_CONNECTIONS_DRAIN_TIME", "10"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """
    Application lifespan context manager.

    This context manager handles startup and shutdown of the application,
    including HTTP client initialization and background task cleanup.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the application after startup.
    """
    global http_client

    # Initialize HTTP client on startup
    http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=5)
    )
    print("Application started, HTTP client initialized")

    # Start background health check task INSIDE the lifespan context
    health_check_task: Optional[asyncio.Task[None]] = None
    if hasattr(health, 'periodic_health_check'):
        health_check_task = asyncio.create_task(health.periodic_health_check())
        print("Background health check task started")

    yield

    # Cancel background tasks during shutdown
    if health_check_task and not health_check_task.done():
        health_check_task.cancel()
        try:
            await health_check_task
        except asyncio.CancelledError:
            print("Health check task cancelled")

    # Close HTTP client
    if http_client:
        await http_client.aclose()
    print("HTTP client closed, shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: A fully configured FastAPI application instance.
    """
    return FastAPI(lifespan=lifespan, redirect_slashes=False)


# Create the FastAPI application
app = create_app()


def setup_signal_handlers() -> asyncio.Event:
    """
    Set up signal handlers for graceful shutdown.

    Registers handlers for SIGTERM and SIGINT signals to initiate
    graceful shutdown when the application receives these signals.

    Returns:
        asyncio.Event: An event that will be set when shutdown is triggered.

    Example:
        >>> shutdown_event = setup_signal_handlers()
        >>> await shutdown_event.wait()
    """
    shutdown_event = asyncio.Event()

    def signal_handler(signum: int, frame: Any) -> None:
        """
        Handle shutdown signals.

        Args:
            signum: The signal number received.
            frame: The current stack frame.
        """
        print(f"Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    return shutdown_event


async def run_with_graceful_shutdown() -> None:
    """
    Run the server with graceful shutdown support.

    This function starts the uvicorn server and waits for shutdown
    signals, then gracefully stops the server by:
    1. Setting should_exit to stop accepting new connections
    2. Waiting for existing connections to drain
    3. Cancelling the server task

    The shutdown timeout can be configured via GRACEFUL_SHUTDOWN_TIMEOUT
    environment variable (default: 30 seconds).
    """
    shutdown_event = setup_signal_handlers()

    # Configure uvicorn server
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8080,
    )
    server = uvicorn.Server(config=config)
    server_task = asyncio.create_task(server.serve())

    # Wait for shutdown signal
    await shutdown_event.wait()

    # Signal server to stop accepting new connections
    server.should_exit = True

    # Wait for connections to drain
    await asyncio.sleep(5)

    # Cancel server task if still running
    if not server_task.done():
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

    print("Shutting down, graceful shutdown complete")


# Add middleware to the application
app.add_middleware(log_middelware.LoggingMiddleware)
app.add_middleware(size_check_middelware.CheckSizeMiddelware)
app.add_middleware(exception_handler.ExceptionHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
router = APIRouter(prefix="/api/v1")
router.include_router(users.router)
router.include_router(products.router)
router.include_router(inventory.router)
router.include_router(metrics.router)

router.include_router(extras.router)

app.include_router(router)

# Set up logging for the main application
setup_logging(logger_name="api_gateway", filename="logs/api_gateway.log")
logger = create_logger(logger_name="api_gateway")


if __name__ == '__main__':
    logger.info("Starting API Gateway")
    asyncio.run(run_with_graceful_shutdown())
    # """
    # Main entry point for running the API Gateway.
    #
    # Executes run_with_graceful_shutdown() to start the server with
    # graceful shutdown handling.
    # """
