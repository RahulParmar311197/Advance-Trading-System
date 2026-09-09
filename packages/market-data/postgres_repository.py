from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from .models import Candle


class PostgresCandleRepository:
    """Small DB-API adapter for the immutable candle table.

    A connection is injected so the package has no hard dependency on a
    particular PostgreSQL driver. The SQL matches infra/database/schema.sql.
    """

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save(self, candles: list[Candle], data_version: str) -> int:
        if not data_version.strip():
            raise ValueError("data_version must not be empty")
        inserted = 0
        with self.connection.cursor() as cursor:
            for candle in candles:
                cursor.execute(
                    """
                    INSERT INTO candles
                      (symbol, timeframe, timestamp, open, high, low, close, volume, data_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timeframe, timestamp) DO NOTHING
                    """,
                    (candle.symbol, candle.timeframe, candle.timestamp,
                     candle.open, candle.high, candle.low, candle.close,
                     candle.volume, data_version),
                )
                inserted += cursor.rowcount
        self.connection.commit()
        return inserted

    def load(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT timestamp, open, high, low, close, volume
                FROM candles
                WHERE symbol=%s AND timeframe=%s AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp
                """,
                (symbol, timeframe, start, end),
            )
            return [
                Candle(
                    timestamp=row[0], symbol=symbol, timeframe=timeframe,
                    open=Decimal(row[1]), high=Decimal(row[2]), low=Decimal(row[3]),
                    close=Decimal(row[4]), volume=Decimal(row[5]),
                )
                for row in cursor.fetchall()
            ]
