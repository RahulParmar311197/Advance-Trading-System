from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from .models import Candle


class CandleRepository(Protocol):
    def save(self, candles: list[Candle], data_version: str) -> int: ...
    def load(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]: ...


class InMemoryCandleRepository:
    """Deterministic repository used by tests and local development.

    Production persistence is supplied separately by the PostgreSQL adapter;
    this implementation intentionally performs no network or database I/O.
    """

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
        rows = [
            candle
            for (row_symbol, row_timeframe, timestamp), (candle, _) in self._rows.items()
            if row_symbol == symbol
            and row_timeframe == timeframe
            and start <= timestamp <= end
        ]
        return sorted(rows, key=lambda c: c.timestamp)
