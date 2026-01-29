# Quick Start Guide

Get your API Gateway up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- pip or poetry for package management
- (Optional) Docker for containerized deployment

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/API-gateway.git
cd API-gateway
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python .\create_venv.py
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python create_venv.py
source ./.venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Gateway

### Development Mode

```bash
# Using uvicorn with auto-reload
python -m uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using the main module (includes graceful shutdown)
python gateway/main.py
```

### Docker

```bash
# Build and run with Docker
docker build -t api-gateway .
docker run -d -p 8000:8000 --name api-gateway api-gateway
```

## Verify Installation

Once running, verify the gateway is working:

```bash
# Health check
curl http://localhost:8000/health/

# Should return: {"status": "ok", "timestamp": "..."}

# Metrics endpoint
curl http://localhost:8000/api/v1/metrics

# Liveness probe
curl http://localhost:8000/health/live
# Should return: {"status": "alive"}
```

## Next Steps

- [Configuration Guide](Configuration) - Customize your setup
- [API Endpoints](User-Routes) - Learn about available endpoints
- [Health Checks](Health-Checks) - Set up health monitoring

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
deactivate 2>/dev/null || true
rm -rf .venv
python create_venv.py
source ./.venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```
