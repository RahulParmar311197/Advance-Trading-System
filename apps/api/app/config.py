from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Advance Trading System")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://ats:ats@localhost:5432/ats")


settings = Settings()
