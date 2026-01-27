import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from logging.config import dictConfig


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage()
        }

        # Include exception information if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def create_logger(logger_name: str = __name__) -> logging.Logger:
    """Create and return a logger with a specified name."""
    return logging.getLogger(name=logger_name)


def setup_logging(logger_name: str = __name__, filename: str = f"logs/{__name__}.log", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5) -> None:
    """Configure logging with JSON formatter and handlers."""
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    log_config = {
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
                "class": RotatingFileHandler,
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
