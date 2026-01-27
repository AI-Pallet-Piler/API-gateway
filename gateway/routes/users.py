import httpx
from fastapi import APIRouter, Response, Request, status

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
            response = client.post(settings.url_backend + "/post")
            if response.status_code == status.HTTP_200_OK:
                logger.debug(response)
                return Response(status_code=status.HTTP_200_OK, content=response.content)
            elif response.status_code == status.HTTP_201_CREATED:
                logger.debug(response)
                return Response(status_code=status.HTTP_201_CREATED, content=response.content)
            elif response.status_code == status.HTTP_202_ACCEPTED:
                logger.debug(response)
                return Response(status_code=status.HTTP_202_ACCEPTED, content=response.content)
            else:
                logger.warning(response.status_code)
                return Response(status_code=status.HTTP_404_NOT_FOUND, content=response.content)
        except httpx.HTTPStatusError as e:
            logger.critical(e)
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=e)


@router.delete("/delete", tags=["users"])
async def delete_user(request: Request):
    with httpx.Client() as client:
        try:
            response = client.delete(settings.url_backend + "/delete")
            if response.status_code == status.HTTP_200_OK:
                logger.warning(response)
                return Response(status_code=status.HTTP_200_OK, content=response.content)
            elif response.status_code == status.HTTP_202_ACCEPTED:
                logger.debug(response)
                return Response(status_code=status.HTTP_202_ACCEPTED, content=response.content)
            elif response.status_code == status.HTTP_204_NO_CONTENT:
                logger.debug(response)
                return Response(status_code=status.HTTP_204_NO_CONTENT, content=response.content)
            else:
                logger.warning(response.status_code)
                return Response(status_code=status.HTTP_404_NOT_FOUND, content=response.content)
        except httpx.HTTPStatusError as e:
            logger.critical(e)
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=e)
