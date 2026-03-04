"""
Middleware module for the API Gateway.

This module provides various middleware components for request/response processing
including logging, exception handling, request ID propagation, and size validation.

Middleware Components:
    exception_handler: Centralized exception handling middleware.
    log_middelware: Request/response logging middleware.
    request_id: Request ID generation and propagation middleware.
    size_check_middelware: Request size validation middleware.

Usage:
    Add middleware to the FastAPI app:
    
    >>> from fastapi import FastAPI
    >>> from gateway.middlewares import exception_handler, log_middelware
    >>> app = FastAPI()
    >>> app.add_middleware(exception_handler.ExceptionHandlingMiddleware)
    >>> app.add_middleware(log_middelware.LoggingMiddleware)
"""

from . import exception_handler
from . import log_middelware
from . import request_id
from . import size_check_middelware

__all__ = [
    "exception_handler",
    "log_middelware", 
    "request_id",
    "size_check_middelware"
]
