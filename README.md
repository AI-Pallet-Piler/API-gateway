# API Gateway (FastAPI)

A production-ready API Gateway built with FastAPI, featuring structured JSON logging, request metrics, health checks, and comprehensive middleware support.

## 🚀 Features

- **HTTP Proxying** - Forward requests to backend services with automatic request ID propagation
- **Structured JSON Logging** - Custom JSON formatter with request tracking
- **Health Checks** - Basic, liveness, and readiness probes for Kubernetes
- **Request Metrics** - Prometheus-compatible metrics with `/metrics` endpoint
- **Request Size Validation** - Protect against large payload attacks
- **Centralized Exception Handling** - Consistent error responses across the gateway
- **Request ID Generation** - Distributed tracing support via `X-Request-ID` header
- **Graceful Shutdown** - Proper cleanup of connections and background tasks
- **CORS Support** - Configurable cross-origin resource sharing

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [Gateway Management](#gateway-management-endpoints)
  - [Backend API Routing](#backend-api-routing)
  - [Security API Routing](#security-api-routing)
- [Middleware](#middleware)
- [Logging](#logging)
- [Metrics](#metrics)
- [Health Checks](#health-checks)
- [Error Handling](#error-handling)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core language |
| FastAPI | Latest | Web framework |
| Uvicorn | Latest | ASGI server |
| HTTPX | Latest | Async HTTP client |
| Pydantic | Latest | Data validation |
| Pydantic Settings | Latest | Configuration management |
| Prometheus Client | Latest | Metrics collection |

## 🏃 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip or poetry for dependency management

### Installation

**Windows (PowerShell):**
```powershell
# Create virtual environment and install dependencies
python .\create_venv.py
\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
# Create virtual environment and install dependencies
python create_venv.py
source ./.venv/bin/activate
pip install -r requirements.txt
```

### Running Locally

```bash
# Using uvicorn directly
python -m uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main module (with graceful shutdown)
python gateway/main.py
```

### Docker

```bash
# Build the image
docker build -t api-gateway .

# Run the container
docker run -d -p 8000:8000 --name api-gateway api-gateway
```

## 📁 Project Structure

```
API-gateway/
├── gateway/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization and setup
│   ├── config.py               # Settings class for configuration
│   ├── loggers/
│   │   ├── __init__.py
│   │   └── logger.py           # JSON formatter and logging setup
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── exception_handler.py  # Centralized exception handling
│   │   ├── log_middelware.py     # Request/response logging
│   │   ├── request_id.py         # Request ID generation
│   │   └── size_check_middelware.py # Request size validation
│   ├── other/
│   │   ├── __init__.py
│   │   └── exceptions.py         # Custom exception classes
│   └── routes/
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── extras.py            # Extra endpoints
│       ├── health.py            # Health check endpoints
│       ├── inventory.py         # Inventory proxy endpoints
│       ├── metrics.py           # Prometheus metrics endpoint
│       ├── navigation.py        # Navigation proxy endpoints
│       ├── orders.py            # Orders proxy endpoints
│       ├── products.py          # Products proxy endpoints
│       ├── reports.py           # Reports proxy endpoints
│       └── users.py             # Users proxy endpoints
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_gateway.py
│   └── test_users.py
├── logs/                        # Log files directory
├── Dockerfile
├── compose.yml
├── prometheus.yml              # Prometheus configuration
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

Configuration is managed via environment variables and `.env` files using Pydantic Settings.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `URL_BACKEND` | Backend service URL | `http://httpbin.org/anything` |
| `SECURITY_API_URL` | Security API URL | `http://security-api:8000` |
| `CHECK_UPSTREAM_SERVICES` | Enable upstream health checks | `false` |
| `GRACEFUL_SHUTDOWN_TIMEOUT` | Shutdown timeout in seconds | `30` |
| `MAX_CONNECTIONS_DRAIN_TIME` | Connection drain time | `10` |

### Example `.env` File

```env
URL_BACKEND=http://backend-service:8000
SECURITY_API_URL=http://security-api:8000
CHECK_UPSTREAM_SERVICES=true
GRACEFUL_SHUTDOWN_TIMEOUT=30
```

## 🔌 API Endpoints

### Gateway Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Basic health check for load balancers |
| `GET` | `/live` | Kubernetes liveness probe |
| `GET` | `/ready` | Kubernetes readiness probe |
| `GET` | `/metrics` | Prometheus metrics endpoint |

### Backend API Routing

The gateway proxies requests to the Backend service (`URL_BACKEND`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/orders` | List all orders with filtering |
| `GET` | `/api/v1/orders/{id}` | Get order by ID |
| `POST` | `/api/v1/orders` | Create a new order |
| `PUT` | `/api/v1/orders/{id}` | Update an order |
| `DELETE` | `/api/v1/orders/{id}` | Delete an order |
| `GET` | `/api/v1/orders/{id}/lines` | Get order lines |
| `GET` | `/api/v1/orders/{id}/pallet-instructions` | Get pallet instructions |
| `POST` | `/api/v1/orders/{id}/trigger-packing` | Trigger packing |
| `GET` | `/api/v1/products` | List all products |
| `GET` | `/api/v1/products/{id}` | Get product by ID |
| `POST` | `/api/v1/products` | Create a new product |
| `PUT` | `/api/v1/products/{id}` | Update a product |
| `DELETE` | `/api/v1/products/{id}` | Delete a product |
| `GET` | `/api/v1/inventory` | List all inventory |
| `GET` | `/api/v1/inventory/{id}` | Get inventory by ID |
| `POST` | `/api/v1/inventory` | Create inventory record |
| `PUT` | `/api/v1/inventory/{id}` | Update inventory |
| `DELETE` | `/api/v1/inventory/{id}` | Delete inventory |
| `GET` | `/api/v1/users` | List all users |
| `GET` | `/api/v1/users/{id}` | Get user by ID |
| `POST` | `/api/v1/users` | Create a new user |
| `PUT` | `/api/v1/users/{id}` | Update a user |
| `DELETE` | `/api/v1/users/{id}` | Delete a user |
| `GET` | `/api/v1/users/badge/{badge_number}` | Get user by badge |
| `GET` | `/api/v1/users/by-email` | Get user by email |
| `GET` | `/api/v1/navigation/map` | Get warehouse map |
| `GET` | `/api/v1/navigation/locations` | Get all locations |
| `GET` | `/api/v1/navigation/path/code/{from}/{to}` | Get path by codes |
| `GET` | `/api/v1/navigation/path/{from_shelf}/{to_shelf}` | Get path by shelf IDs |
| `POST` | `/api/v1/navigation/generate-and-sync` | Generate and sync navigation |
| `GET` | `/api/v1/reports` | List all reports |
| `GET` | `/api/v1/reports/{id}` | Get report by ID |
| `POST` | `/api/v1/reports` | Create a new report |
| `PUT` | `/api/v1/reports/{id}` | Update a report |
| `DELETE` | `/api/v1/reports/{id}` | Delete a report |
| `GET` | `/api/v1/health` | Backend health check |

### Security API Routing

The gateway proxies authentication requests to the Security API (`SECURITY_API_URL`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/v1/login` | Email/password login |
| `POST` | `/auth/v1/login-badge` | Badge-based login |
| `POST` | `/auth/v1/refresh` | Refresh access token |
| `POST` | `/auth/v1/logout` | Logout and invalidate token |
| `POST` | `/auth/v1/validate` | Validate access token |

## 🧩 Middleware

### Request ID Middleware

Generates unique request IDs for each request and propagates them to backend services.

- Extracts `X-Request-ID` header or generates new UUID
- Stores request ID in context variable for async access
- Adds `X-Request-ID` to response headers

### Logging Middleware

Records request metrics including:

- HTTP method
- Endpoint path
- Response status code
- Request duration

### Size Check Middleware

Validates request body size against maximum limit (10MB).

- Returns `413 Payload Too Large` for oversized requests
- Configurable via `MAX_SIZE` constant

### Exception Handling Middleware

Provides centralized exception handling:

- Catches `GatewayException` and subclasses
- Returns standardized JSON error responses
- Logs unexpected exceptions with full tracebacks

## 📝 Logging

### JSON Formatter

Logs are formatted as JSON with the following structure:

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

### Log Files

- Location: `logs/api_gateway.log`
- Rotation: 10MB per file
- Backup count: 10 files

### Logger Usage

```python
from gateway.loggers import setup_logging, create_logger

# Initialize logging (call once at startup)
setup_logging(logger_name="my_module", filename="logs/app.log")

# Create logger for module
logger = create_logger("my_module")

# Use logger
logger.info("Message")
logger.error("Error occurred", exc_info=True)
```

## 📊 Metrics

### Prometheus Metrics

The gateway exposes the following Prometheus metrics:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `gateway_requests_total` | Counter | method, endpoint, status_code | Total requests |
| `gateway_request_duration_seconds` | Histogram | method, endpoint | Request duration |
| `gateway_upstream_requests_total` | Counter | upstream, method, status_code | Upstream requests |
| `gateway_upstream_request_duration_seconds` | Histogram | upstream, method | Upstream duration |
| `gateway_errors_total` | Counter | type, endpoint | Total errors |
| `gateway_active_connections` | Gauge | - | Active connections |

### Accessing Metrics

```bash
# Prometheus format
curl http://localhost:8000/metrics

# JSON format
curl http://localhost:8000/api/v1/metrics/json
```

## 💓 Health Checks

### Basic Health Check (`GET /health`)

Returns basic gateway status.

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Liveness Probe (`GET /live`)

Kubernetes liveness probe - lightweight check.

```json
{
  "status": "alive"
}
```

### Readiness Probe (`GET /ready`)

Kubernetes readiness probe - checks upstream services.

```json
{
  "status": "ready",
  "backend": "connected",
  "security_api": "connected"
}
```

## ⚠️ Error Handling

### Error Codes

| Code | Description |
|------|-------------|
| `AUTH_UNAUTHORIZED` | Authentication required |
| `AUTH_FORBIDDEN` | Access forbidden |
| `AUTH_TOKEN_EXPIRED` | Token has expired |
| `VALIDATION_ERROR` | Request validation failed |
| `REQUEST_TOO_LARGE` | Request body too large |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `UPSTREAM_TIMEOUT` | Upstream service timed out |
| `UPSTREAM_UNAVAILABLE` | Upstream service unavailable |
| `UPSTREAM_ERROR` | Upstream service error |
| `INTERNAL_ERROR` | Internal server error |
| `CONFIGURATION_ERROR` | Configuration error |

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

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t api-gateway .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e URL_BACKEND=http://backend:8000 \
  -e SECURITY_API_URL=http://security-api:8000 \
  --name api-gateway \
  api-gateway
```

### Docker Compose

```yaml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - URL_BACKEND=http://backend-service:8000
      - SECURITY_API_URL=http://security-api:8000
      - CHECK_UPSTREAM_SERVICES=true
    volumes:
      - ./logs:/app/logs
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py
```

### Test Coverage

The project includes unit tests for:

- User routes
- Authentication
- Exception handling
- Middleware functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for your changes
4. Ensure all tests pass (`pytest -q`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Guidelines

- Follow PEP 8 style guide
- Add type annotations to all functions
- Include docstrings for all public functions and classes
- Update documentation for new features
- Add tests for new functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [HTTPX](https://www.python-httpx.org/) for the async HTTP client
- [Prometheus](https://prometheus.io/) for metrics infrastructure
