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
    code_version: str = os.getenv("CODE_VERSION", "api-0.1.0")
    # Format: key_id|organization_id|user_id|role|sha256_digest|active;...
    # Only digests are accepted here; plaintext API-key secrets are never configured or persisted.
    api_key_records: str = os.getenv("API_KEY_RECORDS", "")


settings = Settings()
