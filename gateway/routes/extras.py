"""
Extra routes module for the API Gateway.

This module handles all non defined proxy requests for blocking.
"""
from fastapi import APIRouter

router = APIRouter(tags=["extras"])

@router.get("/")
def get_favicon():
    return None