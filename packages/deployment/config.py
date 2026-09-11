from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


class DeploymentConfigurationError(ValueError):
    """Raised when production deployment configuration is unsafe or incomplete."""


@dataclass(frozen=True, slots=True)
class DeploymentSettings:
    environment: str
    database_url: str
    redis_url: str
    code_version: str
    queue_name: str


def _required_url(name: str, value: str | None, schemes: frozenset[str]) -> str:
    if not value:
        raise DeploymentConfigurationError(f"{name} is required")
    parsed = urlparse(value)
    if parsed.scheme not in schemes or not parsed.netloc:
        allowed = ", ".join(sorted(schemes))
        raise DeploymentConfigurationError(f"{name} must be an absolute URL using {allowed}")
    return value


def load_production_settings(environ: dict[str, str] | None = None) -> DeploymentSettings:
    """Load deployment settings and fail closed when production inputs are missing."""
    env = os.environ if environ is None else environ
    environment = env.get("ENVIRONMENT", "development").strip().lower()
    if environment != "production":
        raise DeploymentConfigurationError("ENVIRONMENT must be production")

    code_version = env.get("CODE_VERSION", "").strip()
    if not code_version:
        raise DeploymentConfigurationError("CODE_VERSION is required")

    queue_name = env.get("QUEUE_NAME", "").strip()
    if not queue_name:
        raise DeploymentConfigurationError("QUEUE_NAME is required")

    return DeploymentSettings(
        environment=environment,
        database_url=_required_url("DATABASE_URL", env.get("DATABASE_URL"), frozenset({"postgresql", "postgres"})),
        redis_url=_required_url("REDIS_URL", env.get("REDIS_URL"), frozenset({"redis", "rediss"})),
        code_version=code_version,
        queue_name=queue_name,
    )
