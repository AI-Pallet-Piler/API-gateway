"""
Logger module for the API Gateway.

This module provides functions for setting up structured JSON logging
and creating named loggers for different components of the gateway.

Functions:
    setup_logging: Configure logging with JSON formatter and rotating file handler.
    create_logger: Create a named logger for a specific module.

Example:
    >>> from gateway.loggers import setup_logging, create_logger
    >>> setup_logging(logger_name="api_gateway", filename="logs/app.log")
    >>> logger = create_logger(__name__)
    >>> logger.info("Application started")
"""

from .logger import setup_logging, create_logger

__all__ = ["setup_logging", "create_logger"]

__version__ = "0.1.0"
