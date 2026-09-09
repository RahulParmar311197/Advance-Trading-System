from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from .models import Candle


class CandleRepository(Protocol):
    def save(self, candles: list[Candle], data_version: str) -> int: ...
    def load(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]: ...


class InMemoryCandleRepository:
    def __init__(self) -> None:
        self._rows: dict[tuple[str, str, datetime], tuple[Candle, str]] = {}

    def save(self, candles: list[Candle], data_version: str) -> int:
        if not data_version.strip():
            raise ValueError("data_version must not be empty")
        inserted = 0
        for candle in candles:
            key = (candle.symbol, candle.timeframe, candle.timestamp)
            if key not in self._rows:
                self._rows[key] = (candle, data_version)
                inserted += 1
        return inserted

    def load(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]:
        return sorted(
            [candle for (s, tf, timestamp), (candle, _) in self._rows.items()
             if s == symbol and tf == timeframe and start <= timestamp <= end],
            key=lambda candle: candle.timestamp,
        )


class PostgresCandleRepository:
    """DB-API adapter matching the project's PostgreSQL candle schema."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save(self, candles: list[Candle], data_version: str) -> int:
        if not data_version.strip():
            raise ValueError("data_version must not be empty")
        inserted = 0
        with self.connection.cursor() as cursor:
            for candle in candles:
                cursor.execute(
                    """INSERT INTO candles
                    (symbol,timeframe,timestamp,open,high,low,close,volume,data_version)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (symbol,timeframe,timestamp) DO NOTHING""",
                    (candle.symbol, candle.timeframe, candle.timestamp, candle.open,
                     candle.high, candle.low, candle.close, candle.volume, data_version),
                )
                inserted += cursor.rowcount
        self.connection.commit()
        return inserted

    def load(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT timestamp,open,high,low,close,volume FROM candles
                WHERE symbol=%s AND timeframe=%s AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp""",
                (symbol, timeframe, start, end),
            )
            from decimal import Decimal
            return [Candle(row[0], symbol, timeframe, *(Decimal(value) for value in row[1:])) for row in cursor.fetchall()]
