from __future__ import annotations

from datetime import datetime

from .models import Candle
from .provider import MarketDataProvider
from .schemas import RawOHLCV


class InMemoryMarketDataProvider(MarketDataProvider):
    """Provider for tests/local demos using explicitly supplied source rows.

    It never generates prices; callers must provide the data.
    """

    def __init__(self, rows: list[RawOHLCV]) -> None:
        self.rows = list(rows)

    def historical_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawOHLCV]:
        return [r for r in self.rows if start <= r.timestamp <= end and r.symbol == symbol and r.timeframe == timeframe]
