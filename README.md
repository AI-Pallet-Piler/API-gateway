# API Gateway (FastAPI) — Lightweight Gateway Service

A minimal FastAPI gateway demonstrating external HTTP calls, structured JSON logging and a small middleware for request/response observability.

## Tech stack
- Python 3.8+
- FastAPI
- uvicorn
- httpx
- logging (custom JSON formatter)
- pip for dependency management

## Quick start (Windows PowerShell)
1. Create and activate venv + dependencies:
   - `python .\create_venv.py`
   - `.\.venv\Scripts\Activate.ps1`
2. Run locally:
   - `.\.venv\Scripts\Activate.ps1`
   - `python -m uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000` or 
   - `python main.py`
3. Example endpoints:
   - `http://localhost:8000/get_first_users`

## Logging
- JSON-formatted logs via `gateway/loggers/logger.py` (`JsonFormatter`).
- Rotating file handlers write into `logs/`.
- Logging is configured by `setup_logging()`; call once at app startup.

## Middleware
- `gateway/loggers/Middelware.py` contains `CustomMiddleware` which logs response metadata.
- Prefer configuring logging at startup (not per-request) for performance.

## Project layout
- `gateway/main.py` — FastAPI app and routes.
- `gateway/loggers/logger.py` — JSON formatter and logging setup.
- `gateway/loggers/Middelware.py` — request/response middleware.
- `tests/` — unit tests (use `pytest`).

## Testing
- Run tests with `pytest -q`.
- Use `TestClient` and mock `httpx` for external calls.

## Contributing
- Fork → branch → tests → PR. Add/update Wiki pages if behavior or endpoints change.

## License
- This repo use under MIT License 
