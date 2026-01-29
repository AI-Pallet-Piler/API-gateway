# Configuration Guide

Learn how to configure the API Gateway using environment variables and configuration files.

## Environment Variables

The gateway uses environment variables for configuration. You can set these in your shell, `.env` file, or container orchestration platform.

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `URL_BACKEND` | string | `""` | Base URL of the backend service |
| `CHECK_UPSTREAM_SERVICES` | boolean | `false` | Enable upstream health checks |
| `GRACEFUL_SHUTDOWN_TIMEOUT` | integer | `30` | Shutdown timeout in seconds |
| `MAX_CONNECTIONS_DRAIN_TIME` | integer | `10` | Connection drain time in seconds |

### Example `.env` File

```env
# Backend configuration
URL_BACKEND=http://backend-service:8000

# Health check settings
CHECK_UPSTREAM_SERVICES=true

# Shutdown settings
GRACEFUL_SHUTDOWN_TIMEOUT=30
MAX_CONNECTIONS_DRAIN_TIME=10
```

## Settings Class

Configuration is managed via the [`Settings`](gateway/config.py:4) class which extends `pydantic_settings.BaseSettings`:

```python
from gateway.config import Settings

settings = Settings()

# Access configuration
print(settings.url_backend)  # "http://backend-service:8000"
print(settings.check_upstream_services)  # True
```

## Backend Service Configuration

### Single Backend

Set the `URL_BACKEND` environment variable to point to your backend service:

```env
URL_BACKEND=http://my-backend-service:8000
```

### Multiple Backends

For multiple backend services, configure routing in your application code or use a service mesh.

## Upstream Health Checks

When `CHECK_UPSTREAM_SERVICES` is enabled, the gateway will check upstream service health during readiness probes.

Configure upstream services in [`gateway/routes/health.py`](gateway/routes/health.py:10):

```python
UPSTREAM_SERVICES = {
    "users_service": {"url": "http://users-service:8000/health", "timeout": 5.0},
    "auth_service": {"url": "http://auth-service:8001/health", "timeout": 5.0},
}
```

## CORS Configuration

Configure CORS in [`gateway/main.py`](gateway/main.py:89):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Logging Configuration

Configure logging in [`gateway/loggers/logger.py`](gateway/loggers/logger.py:38):

```python
setup_logging(
    logger_name="api_gateway",
    filename="logs/api_gateway.log",
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)
```

## Production Considerations

### Security

```env
# Use specific origins in production
ALLOW_ORIGINS=https://your-domain.com

# Restrict methods and headers
ALLOW_METHODS=GET,POST,PUT,DELETE
ALLOW_HEADERS=Content-Type,Authorization
```

### Performance

```env
# Increase connection limits
MAX_CONNECTIONS_DRAIN_TIME=30

# Optimize health checks
GRACEFUL_SHUTDOWN_TIMEOUT=60
```

## Docker/Container Configuration

### Docker Run

```bash
docker run -d \
  -p 8000:8000 \
  -e URL_BACKEND=http://backend:8000 \
  -e CHECK_UPSTREAM_SERVICES=true \
  -e GRACEFUL_SHUTDOWN_TIMEOUT=30 \
  api-gateway
```

### Docker Compose

```yaml
version: '3.8'

services:
  api-gateway:
    image: api-gateway
    ports:
      - "8000:8000"
    environment:
      - URL_BACKEND=http://backend-service:8000
      - CHECK_UPSTREAM_SERVICES=true
      - GRACEFUL_SHUTDOWN_TIMEOUT=30
    volumes:
      - ./logs:/app/logs
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-gateway-config
data:
  URL_BACKEND: "http://backend-service:8000"
  CHECK_UPSTREAM_SERVICES: "true"
  GRACEFUL_SHUTDOWN_TIMEOUT: "30"
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  template:
    spec:
      containers:
      - name: api-gateway
        image: api-gateway
        envFrom:
        - configMapRef:
            name: api-gateway-config
```
