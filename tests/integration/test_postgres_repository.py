from datetime import datetime, timezone
from decimal import Decimal
import os

import psycopg
import pytest

from packages.market_data.models import Candle
from packages.market_data.repository import PostgresCandleRepository


@pytest.fixture
def database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql://ats:ats@localhost:5432/ats")


def test_postgres_candle_repository_persists_idempotently(database_url: str) -> None:
    try:
        connection = psycopg.connect(database_url, connect_timeout=2)
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostgreSQL is not available: {exc}")

    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS candles")
            cursor.execute(
                """CREATE TABLE candles (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    open NUMERIC NOT NULL,
                    high NUMERIC NOT NULL,
                    low NUMERIC NOT NULL,
                    close NUMERIC NOT NULL,
                    volume NUMERIC NOT NULL,
                    data_version TEXT NOT NULL,
                    PRIMARY KEY(symbol, timeframe, timestamp)
                )"""
            )
        connection.commit()

        timestamp = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
        candle = Candle(
            timestamp,
            "NIFTY",
            "5m",
            Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"), Decimal("1000"),
        )
        repository = PostgresCandleRepository(connection)
        assert repository.save([candle], "fixture-v1") == 1
        assert repository.save([candle], "fixture-v1") == 0

        rows = repository.load("NIFTY", "5m", timestamp, timestamp)
        assert rows == [candle]
    finally:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS candles")
        connection.commit()
        connection.close()
