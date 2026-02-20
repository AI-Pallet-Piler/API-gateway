# Logging

The API Gateway uses structured JSON logging for consistent, machine-parseable log output.

## Log Format

All logs are formatted as JSON with the following structure:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "api_gateway",
  "module": "main",
  "line": 42,
  "message": "Request processed",
  "request_id": "abc-123-xyz"
}
```

### Log Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 formatted timestamp |
| `level` | string | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `logger` | string | Name of the logger |
| `module` | string | Python module name |
| `line` | integer | Line number in source file |
| `message` | string | Log message |
| `request_id` | string | Request ID for tracing (or "N/A") |
| `exception` | string | Exception traceback (if present) |

## Configuration

### Setup Logging

Initialize logging at application startup:

```python
from gateway.loggers import setup_logging, create_logger

# Configure logging (call once at startup)
setup_logging(
    logger_name="api_gateway",
    filename="logs/api_gateway.log",
    max_bytes=10 * 1024 * 1024,  # 10MB per file
    backup_count=5                # Keep 5 backup files
)

# Create logger for module
logger = create_logger("my_module")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logger_name` | string | `"__main__"` | Name of the logger to configure |
| `filename` | string | `None` | Path to log file (None = console only) |
| `max_bytes` | int | 10MB | Maximum size per log file |
| `backup_count` | int | 5 | Number of backup files to keep |

## Using the Logger

### Basic Logging

```python
from gateway.loggers import create_logger

logger = create_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Logging with Exception

```python
try:
    # Some code that might fail
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # exc_info=True includes the traceback
```

### Structured Logging

The JSON formatter automatically adds context:

```python
logger.info("User action", extra={"user_id": "123"})
# Output includes: {"message": "User action", "user_id": "123", ...}
```

## Log Files

### Location

Logs are written to `logs/api_gateway.log` by default.

### Rotation

- Maximum file size: 10MB
- Backup count: 5 files
- Files are named: `api_gateway.log`, `api_gateway.log.1`, `api_gateway.log.2`, etc.

### Directory Structure

```
logs/
├── api_gateway.log       # Current log file
├── api_gateway.log.1     # Previous rotation
├── api_gateway.log.2
├── api_gateway.log.3
├── api_gateway.log.4
└── api_gateway.log.5     # Oldest
```

## Log Levels

| Level | Numeric Value | Use Case |
|-------|---------------|----------|
| `DEBUG` | 10 | Detailed debugging information |
| `INFO` | 20 | General informational messages |
| `WARNING` | 30 | Warning messages |
| `ERROR` | 40 | Errors and failures |
| `CRITICAL` | 50 | Critical errors |

### Setting Log Level

```python
# In setup_logging, the logger is set to DEBUG by default
# To change, modify the log_config dictionary
log_config = {
    ...
    "loggers": {
        logger_name: {
            "handlers": ["rotating_file"],
            "level": "DEBUG",  # Change this to INFO, WARNING, etc.
            "propagate": False,
        },
    },
    ...
}
```

## Request ID in Logs

The [`get_request_id()`](gateway/middlewares/request_id.py:33) function retrieves the current request ID from the context:

```python
from gateway.middlewares.request_id import get_request_id

request_id = get_request_id()  # Returns "abc-123-xyz" or ""
```

This is automatically included in all log messages.

## Log Aggregation

### Elasticsearch/Fluentd

Since logs are JSON-formatted, they can be easily ingested into log aggregation systems:

```json
{"timestamp": "...", "level": "INFO", "message": "...", ...}
```

### Example: Parsing with jq

```bash
cat logs/api_gateway.log | jq '.'
```

### Example: Filtering by Level

```bash
cat logs/api_gateway.log | jq 'select(.level == "ERROR")'
```

## Best Practices

1. **Use Appropriate Levels**: Don't log everything at INFO level
2. **Include Context**: Add request IDs, user IDs, etc.
3. **Avoid Sensitive Data**: Don't log passwords, tokens, or PII
4. **Rotate Logs**: Ensure log rotation is configured
5. **Monitor Log Size**: Watch disk usage in production

## Troubleshooting

### No Logs Appearing

1. Check the `logs/` directory exists
2. Verify file permissions
3. Ensure `setup_logging()` was called at startup

### Logs Not in JSON Format

1. Check for other logging configuration
2. Ensure no other handlers are added after `setup_logging()`
3. Verify the `JsonFormatter` is being used

### Missing Request ID

1. Ensure `RequestIDMiddleware` is added
2. Check the request context is active
3. Verify `get_request_id()` is called within a request handler
