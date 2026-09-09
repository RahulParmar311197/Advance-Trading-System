from __future__ import annotations

from datetime import datetime

from .provider import MarketDataProvider
from .schemas import RawOHLCV


class StaticOHLCVProvider(MarketDataProvider):
    """Provider backed only by caller-supplied source rows."""

    def __init__(self, rows: list[RawOHLCV]) -> None:
        self._rows = tuple(rows)

    def historical_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawOHLCV]:
        return [r for r in self._rows if r.symbol == symbol and r.timeframe == timeframe and start <= r.timestamp <= end]
