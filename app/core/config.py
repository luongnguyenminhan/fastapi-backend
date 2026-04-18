import secrets
from typing import Annotated

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_core import MultiHostUrl
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

    # Database Configuration
    MYSQL_SERVER: str = "db"  # External database server
    MYSQL_PORT: int = 3306  # External database port
    MYSQL_USER: str = "admin"
    MYSQL_PASSWORD: str = "admin123"
    MYSQL_DB: str = "meetagent"

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MinIO Configuration
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "meetagent-files"
    MINIO_PUBLIC_BUCKET_NAME: str = "meetagent-public"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"  # Public URL for permanent links (internal Docker network)
    LOG_LEVEL: str = "DEBUG"

    # Gmail API Configuration
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""

    # Admin Configuration
    ADMIN_USER_IDS: list = [2, 20]  # Default admin is user_id=1; override via ADMIN_USER_IDS env var (comma-separated)
    ADMIN_USERNAME: str = "admin"  # Admin login username
    ADMIN_PASSWORD: str = "admin123"  # Admin login password

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @computed_field
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def PROXY_URL(self) -> str:
        """Construct proxy URL from PROXY_HOST and PROXY_PORT."""
        return f"http://{self.PROXY_HOST}:{self.PROXY_PORT}"


settings = Settings()
