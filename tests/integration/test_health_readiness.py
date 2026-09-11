from fastapi.testclient import TestClient

from apps.api.app.config import settings
from apps.api.app.dependencies import get_connection
from apps.api.app.main import app


class Cursor:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query):
        assert query == "SELECT 1"

    def fetchone(self):
        return (1,)


class Database:
    def cursor(self):
        return Cursor()


class Redis:
    def ping(self):
        return True

    def llen(self, key):
        assert key == "ats:jobs:default"
        return 2


def test_readiness_reports_dependencies(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "redis://test")
    monkeypatch.setattr("apps.api.app.routes.health.redis.Redis.from_url", lambda *_args, **_kwargs: Redis())
    app.dependency_overrides[get_connection] = lambda: Database()
    try:
        response = TestClient(app).get("/health/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["components"]["queue"]["detail"] == "depth=2"
    finally:
        app.dependency_overrides.clear()


def test_readiness_fails_closed_without_redis(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", None)
    app.dependency_overrides[get_connection] = lambda: Database()
    try:
        response = TestClient(app).get("/health/ready")
        assert response.status_code == 503
        body = response.json()
        assert body["components"]["redis"]["detail"] == "REDIS_URL is not configured"
        assert body["components"]["queue"]["status"] == "error"
    finally:
        app.dependency_overrides.clear()
