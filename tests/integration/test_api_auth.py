import hashlib

from fastapi.testclient import TestClient

from apps.api.app import auth
from apps.api.app.main import app
from packages.saas.auth import APIKeyAuthenticator, APIKeyRecord, Role


SECRET = "integration-test-secret"


def _set_authenticator() -> None:
    auth._AUTHENTICATOR = APIKeyAuthenticator(
        {
            "viewer-key": APIKeyRecord(
                key_id="viewer-key",
                organization_id="org-a",
                user_id="user-viewer",
                role=Role.VIEWER,
                secret_digest=hashlib.sha256(SECRET.encode()).hexdigest(),
            ),
            "research-key": APIKeyRecord(
                key_id="research-key",
                organization_id="org-a",
                user_id="user-researcher",
                role=Role.RESEARCHER,
                secret_digest=hashlib.sha256(SECRET.encode()).hexdigest(),
            ),
        }
    )


def test_protected_market_route_rejects_missing_credentials() -> None:
    client = TestClient(app)
    response = client.get("/market-data/validate-symbol/NIFTY")

    assert response.status_code == 401
    assert response.json() == {"detail": "authentication required"}
    assert response.headers["www-authenticate"] == "API-Key"


def test_protected_market_route_rejects_invalid_credentials() -> None:
    _set_authenticator()
    client = TestClient(app)
    response = client.get(
        "/market-data/validate-symbol/NIFTY",
        headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": "wrong"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid API key"}


def test_viewer_can_read_market_route() -> None:
    _set_authenticator()
    client = TestClient(app)
    response = client.get(
        "/market-data/validate-symbol/NIFTY",
        headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": SECRET},
    )

    assert response.status_code == 200
    assert response.json() == {"symbol": "NIFTY"}


def test_research_permission_is_required_for_backtest_validation() -> None:
    _set_authenticator()
    client = TestClient(app)
    payload = {
        "start": "2026-01-01T09:15:00+05:30",
        "end": "2026-01-01T10:00:00+05:30",
    }

    viewer_response = client.post(
        "/backtest/validate",
        json=payload,
        headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": SECRET},
    )
    researcher_response = client.post(
        "/backtest/validate",
        json=payload,
        headers={"X-API-Key-ID": "research-key", "X-API-Key-Secret": SECRET},
    )

    assert viewer_response.status_code == 403
    assert researcher_response.status_code == 200
    assert researcher_response.json()["accepted"] is True


def test_health_remains_public() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
