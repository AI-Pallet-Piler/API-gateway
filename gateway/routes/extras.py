"""
Extra routes module for the API Gateway.

This module handles additional routes that don't fit into other categories,
such as the favicon endpoint.

Routes:
    GET / - Favicon endpoint (returns None)

Usage:
    Include this router in main.py:
    
    >>> from gateway.routes.extras import router
    >>> app.include_router(router)
"""

from fastapi import APIRouter

router = APIRouter(tags=["extras"])


@router.get("/")
def get_favicon():
    """
    Favicon endpoint.
    
    Returns None to satisfy favicon requests. This endpoint handles
    browser requests for favicon.ico without returning an error.
    
    Returns:
        None: Returns None for the favicon request.
    
    Note:
        Browsers automatically request /favicon.ico when loading a website.
        Returning None (204 No Content) is the preferred way to handle this.
    
    Example:
        >>> curl -I http://localhost:8080/
    """
    return None
