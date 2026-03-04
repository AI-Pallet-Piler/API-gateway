"""
Routes module for the API Gateway.

This module provides all the route handlers for the gateway, including:
    auth: Authentication endpoints (login, logout, refresh, validate).
    extras: Extra endpoints (favicon, etc.).
    health: Health check endpoints (health, live, ready).
    inventory: Inventory proxy endpoints.
    metrics: Prometheus metrics endpoint.
    navigation: Warehouse navigation proxy endpoints.
    orders: Orders proxy endpoints.
    products: Products proxy endpoints.
    reports: Reports proxy endpoints.
    users: Users proxy endpoints.

Usage:
    Import routes in main.py:
    
    >>> from gateway.routes import users, products, orders, health
    >>> app.include_router(users.router, prefix="/api/v1")
"""

from . import auth
from . import extras
from . import health
from . import inventory
from . import metrics
from . import navigation
from . import orders
from . import products
from . import reports
from . import users

__all__ = [
    "auth",
    "extras",
    "health",
    "inventory",
    "metrics",
    "navigation",
    "orders",
    "products",
    "reports",
    "users"
]
