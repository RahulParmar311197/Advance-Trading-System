from pathlib import Path

import pytest

from packages.deployment.config import DeploymentConfigurationError, load_production_settings


COMPOSE_FILE = Path(__file__).parents[2] / "infra" / "deployment" / "docker-compose.production.yml"


def _valid_env() -> dict[str, str]:
    return {
        "ENVIRONMENT": "production",
        "DATABASE_URL": "postgresql://user:secret@db:5432/ats",
        "REDIS_URL": "redis://redis:6379/0",
        "CODE_VERSION": "git-abc123",
        "QUEUE_NAME": "default",
    }


def test_production_configuration_loads_only_from_explicit_environment() -> None:
    settings = load_production_settings(_valid_env())

    assert settings.environment == "production"
    assert settings.database_url.startswith("postgresql://")
    assert settings.redis_url.startswith("redis://")
    assert settings.code_version == "git-abc123"


@pytest.mark.parametrize("missing", ["DATABASE_URL", "REDIS_URL", "CODE_VERSION", "QUEUE_NAME"])
def test_production_configuration_fails_closed_when_required_value_is_missing(missing: str) -> None:
    environment = _valid_env()
    environment.pop(missing)

    with pytest.raises(DeploymentConfigurationError, match=missing):
        load_production_settings(environment)


def test_production_configuration_rejects_non_production_environment() -> None:
    environment = _valid_env()
    environment["ENVIRONMENT"] = "development"

    with pytest.raises(DeploymentConfigurationError, match="production"):
        load_production_settings(environment)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("DATABASE_URL", "redis://user:secret@db:5432/ats"),
        ("DATABASE_URL", "https://db.example/ats"),
        ("REDIS_URL", "postgresql://redis:secret@redis:6379/0"),
        ("REDIS_URL", "https://redis.example/0"),
    ],
)
def test_production_configuration_rejects_wrong_service_url_scheme(name: str, value: str) -> None:
    environment = _valid_env()
    environment[name] = value

    with pytest.raises(DeploymentConfigurationError, match=name):
        load_production_settings(environment)


def test_production_configuration_accepts_tls_redis() -> None:
    environment = _valid_env()
    environment["REDIS_URL"] = "rediss://redis.example:6380/0"

    settings = load_production_settings(environment)

    assert settings.redis_url.startswith("rediss://")


def test_production_api_healthcheck_requires_dependency_readiness() -> None:
    compose = COMPOSE_FILE.read_text(encoding="utf-8")

    assert "urlopen('http://127.0.0.1:8000/health/ready', timeout=3)" in compose
    assert "urlopen('http://127.0.0.1:8000/health', timeout=3)" not in compose
