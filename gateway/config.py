from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url_backend: str = ""

    model_config = SettingsConfigDict(env_file="../.env")