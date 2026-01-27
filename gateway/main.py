import uvicorn
from fastapi import FastAPI, APIRouter

from gateway.loggers import setup_logging, create_logger
from gateway.middelwares import log_middelware
from gateway.routes import users

app = FastAPI(prefix="/api/v1")
# app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

app.add_middleware(log_middelware.Logging_middelware)

router = APIRouter(prefix="/api/v1")
router.include_router(users.router)

app.include_router(router)

# Apply the configuration
setup_logging(logger_name="api_gateway", filename="logs/api_gateway.log")
logger = create_logger(logger_name="api_gateway")



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)