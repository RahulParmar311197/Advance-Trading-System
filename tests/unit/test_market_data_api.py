from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from apps.api.app.routes.market_data import candles


class Cursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params):
        self.executed = (query, params)

    def fetchall(self):
        return self.rows


class Connection:
    def __init__(self, rows):
        self.cursor_instance = Cursor(rows)

    def cursor(self):
        return self.cursor_instance


def test_candles_endpoint_reads_ordered_rows_from_repository_schema() -> None:
    timestamp = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    end = timestamp + timedelta(minutes=5)
    connection = Connection([(timestamp, Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"), Decimal("1000"))])

    result = candles(
        symbol="NIFTY",
        timeframe="5m",
        start=timestamp,
        end=end,
        limit=100,
        connection=connection,
    )

    assert len(result) == 1
    assert result[0].symbol == "NIFTY"
    assert result[0].close == Decimal("101")
    assert connection.cursor_instance.executed[1] == ("NIFTY", "5m", timestamp, end, 100)


def test_candles_endpoint_rejects_reversed_range() -> None:
    start = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 9, tzinfo=timezone.utc)
    with pytest.raises(Exception, match="end must be after start"):
        candles("NIFTY", "5m", start, end, 100, Connection([]))


def test_candles_endpoint_rejects_empty_range() -> None:
    timestamp = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    with pytest.raises(Exception, match="end must be after start"):
        candles("NIFTY", "5m", timestamp, timestamp, 100, Connection([]))
