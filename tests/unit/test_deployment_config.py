import pytest

from packages.deployment.config import DeploymentConfigurationError, load_production_settings


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


def test_production_configuration_rejects_malformed_service_urls() -> None:
    environment = _valid_env()
    environment["DATABASE_URL"] = "not-a-url"

    with pytest.raises(DeploymentConfigurationError, match="DATABASE_URL"):
        load_production_settings(environment)
