import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import psycopg
import pytest


class _Cursor:
    def __init__(self) -> None:
        self.query = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return [
            (
                datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc),
                Decimal("100"),
                Decimal("101"),
                Decimal("99"),
                Decimal("100.5"),
                Decimal("10"),
            )
        ]


class _Connection:
    def __init__(self) -> None:
        self.cursor_instance = _Cursor()

    def cursor(self):
        return self.cursor_instance


def test_api_module_imports():
    from apps.api.app.main import app

    paths = set(app.openapi()["paths"])
    assert "/health" in paths
    assert "/market-data/candles" in paths
    assert "/market-data/smc-events" in paths
    assert "/backtest/run" in paths
    assert "/experiments" in paths
    assert "/experiments/{experiment_id}" in paths
    assert "/experiments/{experiment_id}/rerun" in paths


def test_api_allows_local_dashboard_origin():
    from apps.api.app.main import app

    middleware = next(item for item in app.user_middleware if item.cls.__name__ == "CORSMiddleware")
    assert "http://localhost:3000" in middleware.kwargs["allow_origins"]
    assert "GET" in middleware.kwargs["allow_methods"]
    assert "POST" in middleware.kwargs["allow_methods"]


def test_market_data_queries_use_half_open_time_window():
    from apps.api.app.routes.market_data import _load_candles

    connection = _Connection()
    start = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 9, 20, tzinfo=timezone.utc)

    candles = _load_candles(connection, "NIFTY", "5m", start, end, 100)

    assert len(candles) == 1
    assert "timestamp >= %s" in connection.cursor_instance.query
    assert "timestamp < %s" in connection.cursor_instance.query
    assert "BETWEEN" not in connection.cursor_instance.query
    assert connection.cursor_instance.params == ("NIFTY", "5m", start, end, 100)


def test_market_data_window_rejects_naive_start():
    from apps.api.app.routes.market_data import _validate_window

    with pytest.raises(HTTPException, match="start must be timezone-aware"):
        _validate_window(datetime(2026, 1, 1, 9, 15), datetime(2026, 1, 1, 9, 20, tzinfo=timezone.utc))


def test_market_data_window_rejects_naive_end():
    from apps.api.app.routes.market_data import _validate_window

    with pytest.raises(HTTPException, match="end must be timezone-aware"):
        _validate_window(datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc), datetime(2026, 1, 1, 9, 20))


def test_database_operational_failure_returns_fail_closed_503():
    from apps.api.app.main import handle_database_unavailable

    request = Request({"type": "http", "method": "GET", "path": "/health", "headers": []})
    response = asyncio.run(
        handle_database_unavailable(request, psycopg.OperationalError("connection refused"))
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 503
    assert response.body == b'{"detail":"database unavailable","error":"OperationalError"}'


def test_database_timeout_returns_same_fail_closed_response():
    from apps.api.app.main import handle_database_unavailable

    request = Request({"type": "http", "method": "GET", "path": "/health", "headers": []})
    response = asyncio.run(
        handle_database_unavailable(request, psycopg.OperationalError("connection timed out"))
    )

    assert response.status_code == 503
    assert response.body == b'{"detail":"database unavailable","error":"OperationalError"}'
