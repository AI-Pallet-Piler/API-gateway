# Health Checks

The API Gateway provides three types of health check endpoints designed for different use cases.

## Endpoints Overview

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `GET /health/` | Basic health | General monitoring |
| `GET /health/live` | Liveness probe | Kubernetes liveness |
| `GET /health/ready` | Readiness probe | Kubernetes readiness |

## Basic Health Check

**Endpoint:** `GET /health/`

Returns a simple status check to verify the gateway is responding.

### Request

```bash
curl http://localhost:8000/health/
```

### Response

```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Use Cases

- Load balancer health checks
- General monitoring
- Alerting systems

## Liveness Probe

**Endpoint:** `GET /health/live`

Kubernetes liveness probe - should respond quickly without checking dependencies.

### Request

```bash
curl http://localhost:8000/health/live
```

### Response

```json
{
  "status": "alive"
}
```

### Use Cases

- Kubernetes liveness probes
- Container orchestrator health checks
- Quick uptime verification

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: api-gateway
    image: api-gateway
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30
```

## Readiness Probe

**Endpoint:** `GET /health/ready`

Kubernetes readiness probe - checks if the gateway can accept traffic by verifying upstream services.

### Request

```bash
curl http://localhost:8000/health/ready
```

### Response (Healthy)

```json
{
  "status": "healthy",
  "components": {
    "users_service": {"status": "healthy"},
    "auth_service": {"status": "healthy"}
  }
}
```

### Response (Degraded)

```json
{
  "status": "degraded",
  "components": {
    "users_service": {"status": "healthy"},
    "auth_service": {"status": "unhealthy", "error": "Connection timeout"}
  }
}
```

### Status Codes

- `200`: All services healthy
- `503`: One or more services unhealthy

### Upstream Services Configuration

Configure upstream services in [`gateway/routes/health.py`](gateway/routes/health.py:10):

```python
UPSTREAM_SERVICES = {
    "users_service": {
        "url": "http://users-service:8000/health",
        "timeout": 5.0
    },
    "auth_service": {
        "url": "http://auth-service:8001/health",
        "timeout": 5.0
    },
}
```

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: api-gateway
    image: api-gateway
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
```

## Periodic Background Health Checks

The gateway can run periodic health checks in the background:

```python
# Automatic when enabled in configuration
async def periodic_health_check():
    while True:
        await readiness()  # Updates health_status dict
        await asyncio.sleep(30)  # Check every 30 seconds
```

## Health Status Object

The gateway maintains an in-memory health status:

```python
health_status = {
    "status": "healthy",  # "healthy" or "degraded"
    "timestamp": "2024-01-15T10:30:00.000Z",
    "components": {
        "users_service": {"status": "healthy"},
        "auth_service": {"status": "healthy"}
    }
}
```

## Best Practices

1. **Liveness Probe**: Keep it fast and simple - only check if the process is running
2. **Readiness Probe**: Check dependencies - database, upstream services, etc.
3. **Timing**: Set appropriate `initialDelaySeconds` to avoid premature failures
4. **Thresholds**: Configure `failureThreshold` based on your restart policy

## Monitoring

Prometheus metrics for health checks are available at `/api/v1/metrics`:

```promql
# Health check request rate
rate(gateway_requests_total{endpoint="/health/ready"}[5m])

# Health check error rate
rate(gateway_errors_total{endpoint="/health/ready"}[5m])
```
