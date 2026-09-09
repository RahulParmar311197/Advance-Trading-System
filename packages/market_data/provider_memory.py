from __future__ import annotations

from datetime import datetime

from .provider import MarketDataProvider
from .schemas import RawOHLCV


class InMemoryMarketDataProvider(MarketDataProvider):
    """Deterministic provider backed only by caller-supplied source rows."""

    def __init__(self, rows: list[RawOHLCV]) -> None:
        self.rows = list(rows)

    def historical_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[RawOHLCV]:
        return [
            row
            for row in self.rows
            if start <= row.timestamp <= end
            and row.symbol == symbol
            and row.timeframe == timeframe
        ]
