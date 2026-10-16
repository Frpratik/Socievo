"""Application configuration using Pydantic Settings v2."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application settings
    APP_NAME: str = "Socievo"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "insecure-dev-secret-key-change-in-production-min-32-chars-long"

    # URL & Networking
    ALLOWED_HOSTS: Union[List[str], str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    @field_validator("ALLOWED_HOSTS", "CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Database configuration
    POSTGRES_USER: str = "socievo_user"
    POSTGRES_PASSWORD: str = "socievo_password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "socievo_db"
    
    # Defaults to PostgreSQL, but allows fallback or test in-memory/file SQLite
    DATABASE_URL: str = "postgresql+asyncpg://socievo_user:socievo_password@localhost:5432/socievo_db"
    DATABASE_URL_SYNC: str = "postgresql://socievo_user:socievo_password@localhost:5432/socievo_db"

    # Cache & Queues (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security & Tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # Payments
    PAYMENT_MODE: str = "mock"  # "mock" or "razorpay"
    RAZORPAY_KEY_ID: str = "rzp_test_placeholder_key_id"
    RAZORPAY_KEY_SECRET: str = "rzp_test_placeholder_key_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "rzp_test_webhook_secret_key"

    # Financial defaults
    PLATFORM_DEFAULT_CURRENCY: str = "INR"
    PLATFORM_DEFAULT_COMMISSION_PERCENTAGE: float = 10.0
    PLATFORM_TAX_PERCENTAGE: float = 18.0

    # Storage
    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./uploads"


settings = Settings()
