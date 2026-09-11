import hashlib

from fastapi.testclient import TestClient

from apps.api.app.main import app
from packages.saas.auth import Role


SECRET = "integration-test-secret"


class FakeCursor:
    def __init__(self, row):
        self.row = row

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, _query, _params):
        return None

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row=None):
        self.row = row

    def cursor(self):
        return FakeCursor(self.row)

    def close(self):
        return None


def _use_db_key(row):
    from apps.api.app.dependencies import get_connection

    app.dependency_overrides[get_connection] = lambda: FakeConnection(row)


def _clear_overrides():
    app.dependency_overrides.clear()


def test_protected_market_route_rejects_missing_credentials():
    _use_db_key(None)
    try:
        client = TestClient(app)
        response = client.get("/market-data/validate-symbol/NIFTY")
        assert response.status_code == 401
        assert response.json() == {"detail": "authentication required"}
        assert response.headers["www-authenticate"] == "API-Key"
    finally:
        _clear_overrides()


def test_protected_market_route_rejects_invalid_credentials():
    digest = hashlib.sha256(SECRET.encode()).hexdigest()
    _use_db_key(("viewer-key", "org-a", "user-viewer", Role.VIEWER.value, digest, True))
    try:
        client = TestClient(app)
        response = client.get(
            "/market-data/validate-symbol/NIFTY",
            headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": "wrong"},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "invalid API key"}
    finally:
        _clear_overrides()


def test_persistent_viewer_can_read_market_route():
    digest = hashlib.sha256(SECRET.encode()).hexdigest()
    _use_db_key(("viewer-key", "org-a", "user-viewer", Role.VIEWER.value, digest, True))
    try:
        client = TestClient(app)
        response = client.get(
            "/market-data/validate-symbol/NIFTY",
            headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": SECRET},
        )
        assert response.status_code == 200
        assert response.json() == {"symbol": "NIFTY"}
    finally:
        _clear_overrides()


def test_persistent_role_permission_is_required_for_backtest_validation():
    digest = hashlib.sha256(SECRET.encode()).hexdigest()
    _use_db_key(("viewer-key", "org-a", "user-viewer", Role.VIEWER.value, digest, True))
    try:
        client = TestClient(app)
        payload = {
            "start": "2026-01-01T09:15:00+05:30",
            "end": "2026-01-01T10:00:00+05:30",
        }
        response = client.post(
            "/backtest/validate",
            json=payload,
            headers={"X-API-Key-ID": "viewer-key", "X-API-Key-Secret": SECRET},
        )
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_health_remains_public():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
