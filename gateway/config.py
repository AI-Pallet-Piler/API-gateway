"""
Configuration module for the API Gateway.

This module provides the Settings class that loads configuration from
environment variables and .env files using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env files.

    This class uses Pydantic Settings for automatic environment variable
    loading and validation. Configuration values can be set via:
    - Environment variables
    - .env file in the parent directory
    - Default values

    Attributes:
        url_backend: The base URL of the backend service to proxy requests to.
            Defaults to "http://httpbin.org/anything".
        security_api_url: The base URL of the security/auth service.
            Defaults to "http://security-api:8000".
        check_upstream_services: Whether to check upstream service health
            during readiness probes. Defaults to False.

    Example:
        >>> settings = Settings()
        >>> print(settings.url_backend)
        "http://backend-service:8000"
        >>> print(settings.security_api_url)
        "http://security-api:8000"
    """

    url_backend: str = "http://httpbin.org/anything"
    security_api_url: str = "http://security-api:8000"
    check_upstream_services: bool = False

    model_config = SettingsConfigDict(
        extra="ignore"  # Ignore unknown environment variables
    )
