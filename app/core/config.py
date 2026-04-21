import secrets
from typing import Annotated

from pydantic import (
    AnyUrl,
    BeforeValidator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.vault_loader import load_config

load_config()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Server Configuration
    SERVER_NAME: str = "Note-taking API"
    SERVER_HOST: str = "http://localhost"
    SERVER_PORT: int = 8081

    # CORS Configuration
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str,
        BeforeValidator(lambda x: x.split(",") if isinstance(x, str) else x),
    ] = []

    # Project Configuration
    PROJECT_NAME: str = "Note-taking API"

    LOG_LEVEL: str = "DEBUG"

    ADMIN_USERNAME: str = "admin"  # Admin login username
    ADMIN_PASSWORD: str = "admin123"  # Admin login password


settings = Settings()
