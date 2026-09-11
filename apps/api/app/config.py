from __future__ import annotations

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Advance Trading System")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://ats:ats@localhost:5432/ats")
    database_connect_timeout_seconds: int = Field(
        default=int(os.getenv("DATABASE_CONNECT_TIMEOUT_SECONDS", "5")),
        gt=0,
    )
    redis_url: str | None = os.getenv("REDIS_URL")
    code_version: str = os.getenv("CODE_VERSION", "api-0.1.0")


settings = Settings()
