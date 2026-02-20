# Middleware

The API Gateway uses several middleware components to handle cross-cutting concerns.

## Middleware Stack

```
Incoming Request
    ↓
[RequestIDMiddleware]  ← Assigns request ID
    ↓
[CheckSizeMiddelware]  ← Validates request size
    ↓
[LoggingMiddleware]    ← Records metrics
    ↓
[ExceptionHandlingMiddleware] ← Handles errors
    ↓
[Route Handler]        ← Your endpoint logic
    ↓
Response
```

## Request ID Middleware

**File:** [`gateway/middlewares/request_id.py`](gateway/middlewares/request_id.py:12)

The Request ID middleware generates and propagates unique request IDs for distributed tracing.

### Features

- Extracts `X-Request-ID` from incoming request headers
- Generates new UUID if header not present
- Stores request ID in context variable for async access
- Adds `X-Request-ID` to response headers

### Configuration

```python
from gateway.middlewares.request_id import RequestIDMiddleware

# Default configuration (header: X-Request-ID)
app.add_middleware(RequestIDMiddleware)

# Custom header name
app.add_middleware(RequestIDMiddleware, header_name="X-Correlation-ID")
```

### Usage

```python
from gateway.middlewares.request_id import get_request_id

def my_handler():
    request_id = get_request_id()
    print(f"Processing request: {request_id}")
```

## Size Check Middleware

**File:** [`gateway/middlewares/size_check_middelware.py`](gateway/middlewares/size_check_middelware.py:6)

Protects against large payload attacks by validating request body size.

### Features

- Checks `Content-Length` header
- Returns `413 Payload Too Large` for oversized requests
- Default limit: 10MB

### Configuration

```python
from gateway.middlewares.size_check_middelware import CheckSizeMiddelware

app.add_middleware(CheckSizeMiddelware)
```

### Customize Size Limit

```python
# Modify MAX_SIZE in gateway/middlewares/size_check_middelware.py
MAX_SIZE = 5 * 1024 * 1024  # 5MB
```

## Logging Middleware

**File:** [`gateway/middlewares/log_middelware.py`](gateway/middlewares/log_middelware.py:9)

Records request metrics for monitoring and observability.

### Features

- Measures request duration
- Records method, endpoint, and status code
- Integrates with Prometheus metrics

### Usage

```python
from gateway.middlewares.log_middelware import LoggingMiddleware

app.add_middleware(LoggingMiddleware)
```

## Exception Handling Middleware

**File:** [`gateway/middlewares/exception_handler.py`](gateway/middlewares/exception_handler.py:9)

Provides centralized exception handling with consistent error responses.

### Features

- Catches `GatewayException` and subclasses
- Returns standardized JSON error responses
- Logs unexpected exceptions with full tracebacks
- Includes request ID in error responses

### Error Response Format

```json
{
  "error": "error",
  "code": "UPSTREAM_UNAVAILABLE",
  "message": "Backend service is unavailable",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "request_id": "abc-123-xyz",
  "path": "/api/v1/users",
  "details": null
}
```

### Usage

```python
from gateway.middlewares.exception_handler import ExceptionHandlingMiddleware

app.add_middleware(ExceptionHandlingMiddleware)
```

## Adding Custom Middleware

### Functional Middleware

```python
from fastapi import Request, Response

async def custom_middleware(request: Request, call_next):
    # Before request
    print(f"Incoming request: {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # After request
    print(f"Response status: {response.status_code}")
    
    return response

# Add to app
app.middleware("http")(custom_middleware)
```

### Class-Based Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Your logic here
        response = await call_next(request)
        return response

# Add to app
app.add_middleware(CustomMiddleware)
```

## Middleware Order

Middleware order matters! The gateway uses this order:

1. **RequestIDMiddleware** - First to ensure request ID is available
2. **CheckSizeMiddelware** - Early rejection of oversized requests
3. **LoggingMiddleware** - Record metrics for all requests
4. **ExceptionHandlingMiddleware** - Last to catch any errors

```python
# This is the order in gateway/main.py
app.add_middleware(RequestIDMiddleware)
app.add_middleware(CheckSizeMiddelware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionHandlingMiddleware)
```
