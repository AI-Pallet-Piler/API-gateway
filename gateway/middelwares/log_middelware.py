from gateway.loggers.logger import setup_logging, create_logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class Logging_middelware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        setup_logging(logger_name="gateway_endpoints", filename="logs/gateway_endpoints.log")
        logger = create_logger(logger_name="gateway_endpoints")
        response_dict: dict = {}
        # Call the next middleware or endpoint
        response = await call_next(request)
        # if request.method == "GET":
        #     response_dict = {
        #         "body": "no body",
        #     }
        # else:
        #     response_dict = {
        #         "body": response.body,
        #     }
        logger.info(f"Response Type: {type(response).__name__}, Status Code: {response.status_code}")
        # response_dict = {
        #     "status_code": response.status_code,
        #     "headers": response.headers,
        #     "content-type": response.headers["content-type"],
        # }
        logger.info(response_dict)

        return response
