from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    create_url_backend: str = ""

    model_config = SettingsConfigDict(env_file="../.env")