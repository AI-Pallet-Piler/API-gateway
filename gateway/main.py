import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
import rich
from starlette.middleware.base import BaseHTTPMiddleware
from loggers.logger import *
from loggers.Middelware import *

app = FastAPI()
# app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)


app.add_middleware(CustomMiddleware)

# Apply the configuration
setup_logging(logger_name="api_gateway", filename="logs/api_gateway.log")
logger = create_logger(logger_name="api_gateway")

urlbase = "https://jsonplaceholder.typicode.com"

# rich.print(globals())

@app.get('/get_first users')
async def first_user_httpx():  # Unique name
    # logger.info("This is an info message")
    api_url = f"{urlbase}/users"
    with httpx.Client() as client:
        response = client.get(api_url)  # Get response from httpx
        # return type(response)
        all_users = response.json()    # Parse json directly from that response
        user1 = all_users[0]
        # logger.info(f"user1: {user1}")
        return {'name': user1["name"], "email": user1["email"]}

@app.get("/favicon.ico")
async def favicon():
    return None  # Just returns a response without content

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)