from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.api.app.routes.backtest import BacktestRequest, run


def _connection(rows):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    return connection


def _rows():
    base = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    return [
        (base.replace(minute=15 + i * 5), 100 + i, 101 + i, 99 + i, 100 + i, 1000, "fixture-v1")
        for i in range(6)
    ]


def test_run_executes_registered_strategy_and_returns_metrics():
    request = BacktestRequest(
        start=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
        end=datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
    )

    result = run(request, _connection(_rows()))

    assert result["status"] == "completed"
    assert result["data_version"] == "fixture-v1"
    assert result["symbol"] == "NIFTY"
    assert result["timeframe"] == "5m"
    assert result["candle_count"] == 6
    assert result["trade_count"] == 0
    assert result["metrics"]["trade_count"] == 0
    assert result["trades"] == []


def test_run_rejects_mixed_data_versions():
    request = BacktestRequest(
        start=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
        end=datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
    )
    rows = _rows()
    rows[-1] = (*rows[-1][:-1], "fixture-v2")

    with pytest.raises(Exception) as exc_info:
        run(request, _connection(rows))

    assert exc_info.value.status_code == 409


def test_validate_rejects_reversed_range():
    from apps.api.app.routes.backtest import validate_request

    request = BacktestRequest(
        start=datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
        end=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
    )

    with pytest.raises(Exception) as exc_info:
        validate_request(request)

    assert exc_info.value.status_code == 400
