"""
Logging configuration module for the API Gateway.

This module provides custom JSON logging, logger creation, and logging
setup functions for consistent log formatting across the gateway.
"""

import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from logging.config import dictConfig
from typing import Optional, Dict, Any


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging output.

    This formatter converts log records into JSON format with consistent
    fields including timestamp, level, logger name, module, line number,
    message, and request ID for distributed tracing.

    Attributes:
        None (immutable formatting behavior)

    Example:
        >>> import logging
        >>> handler = RotatingFileHandler("app.log")
        >>> handler.setFormatter(JsonFormatter())
        >>> logger = logging.getLogger("my_app")
        >>> logger.addHandler(handler)
        >>> logger.info("Test message")
        # Outputs: {"timestamp": "...", "level": "INFO", ...}
    """

    def _get_request_id(self) -> str:
        """Lazily import and call get_request_id to avoid circular imports."""
        try:
            from gateway.middlewares.request_id import get_request_id
            return get_request_id() or "N/A"
        except Exception:
            return "N/A"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Args:
            record: The logging.LogRecord to format.

        Returns:
            str: A JSON string containing all log fields.
        """
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
            "request_id": self._get_request_id(),  # Add request ID
        }

        # Include exception information if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def create_logger(logger_name: str = "__main__") -> logging.Logger:
    """
    Create and return a logger with the specified name.

    Args:
        logger_name: The name for the logger. Defaults to "__main__".

    Returns:
        logging.Logger: A logger instance with the given name.

    Example:
        >>> logger = create_logger("my_module")
        >>> logger.info("Logger created")
    """
    return logging.getLogger(name=logger_name)


def setup_logging(
    logger_name: str = "__main__",
    filename: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """
    Configure logging with JSON formatter and handlers.

    Sets up a rotating file handler and console handler with JSON
    formatting. The configuration is applied via dictConfig for
    flexible logging setup.

    Args:
        logger_name: The name of the logger to configure.
        filename: Path to the log file. If None, only console logging is used.
        max_bytes: Maximum size of each log file in bytes. Defaults to 10MB.
        backup_count: Number of backup log files to keep. Defaults to 5.

    Raises:
        OSError: If the log directory cannot be created.

    Example:
        >>> setup_logging(
        ...     logger_name="api_gateway",
        ...     filename="logs/api_gateway.log",
        ...     max_bytes=5*1024*1024,
        ...     backup_count=3
        ... )
    """
    # Create log directory if it doesn't exist
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": filename,
                "maxBytes": max_bytes,  # File size limit
                "backupCount": backup_count,  # Number of backup files
            },
        },
        "loggers": {
            logger_name: {
                "handlers": ["rotating_file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
        "root": {
            # "handlers": ["console"],
            "level": "DEBUG",
        },
    }

    dictConfig(log_config)


if __name__ == "__main__":
    setup_logging()
    logging.getLogger().info("Logging initialized.")
