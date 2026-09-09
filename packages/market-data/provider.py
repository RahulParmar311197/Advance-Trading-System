from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from .schemas import RawOHLCV

class MarketDataProvider(ABC):
    @abstractmethod
    def historical_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawOHLCV]:
        """Return provider-sourced raw OHLCV without silently filling missing values."""
