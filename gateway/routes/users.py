import httpx
from fastapi import APIRouter, Response, status

from gateway import config
from gateway.loggers import setup_logging, create_logger

router = APIRouter(prefix="/users", tags=["users"])

settings = config.Settings()
setup_logging(logger_name="users", filename="logs/api_gateway.log")
logger = create_logger(logger_name="users")

@router.post("/create", tags=["users"])
async def create_user():
    with httpx.Client() as client:
        try:
            response = client.post(settings.url_backend)
            if response.status_code == status.HTTP_201_CREATED:
                logger.debug(response)
                return Response(status_code=status.HTTP_201_CREATED, content=response.content)
            else:
                logger.warning(response.status_code)
                return Response(status_code=status.HTTP_404_NOT_FOUND, content=response.content)
        except httpx.HTTPStatusError as e:
            logger.critical(e)
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=e)