import logging
import sys
import json
from datetime import datetime

# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage()
        }
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Define the logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JsonFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {  # This is the handler name
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "fastapi.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "rotating_file"],  # Use "rotating_file" instead of "file"
            "level": "DEBUG",
            "propagate": False
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
