import logging
from logging.config import dictConfig
import uvicorn
from fastapi import FastAPI
import httpx

from gateway.loggers.logger import log_config

app = FastAPI()

# Apply the configuration
dictConfig(log_config)

# Create a logger instance
logger = logging.getLogger("app")

urlbase = "https://jsonplaceholder.typicode.com"

@app.get('/get_first users')
async def first_user_httpx():  # Unique name
    logger.info("This is an info message")
    api_url = f"{urlbase}/users"
    with httpx.Client() as client:
        response = client.get(api_url)  # Get response from httpx
        # return type(response)
        all_users = response.json()    # Parse json directly from that response
        user1 = all_users[0]
        logger.info(f"user1: {user1}")
        return {'name': user1["name"], "email": user1["email"]}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)