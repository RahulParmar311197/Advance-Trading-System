from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from packages.market_data.ingestion import ingest_ohlcv
from packages.market_data.models import Candle
from packages.market_data.provider import MarketDataProvider


@dataclass(frozen=True, slots=True)
class HistoricalDataRequest:
    """Explicit market-data scope requested by the research agent."""

    symbol: str
    timeframe: str
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")
        if self.start > self.end:
            raise ValueError("start must be <= end")


@dataclass(frozen=True, slots=True)
class HistoricalDataResult:
    """Validated candles returned by an explicitly supplied data provider."""

    request: HistoricalDataRequest
    candles: tuple[Candle, ...]


def get_historical_data(
    provider: MarketDataProvider, request: HistoricalDataRequest
) -> HistoricalDataResult:
    """Fetch, normalize, and validate historical candles without synthesizing data."""
    candles = ingest_ohlcv(
        provider,
        request.symbol,
        request.timeframe,
        request.start,
        request.end,
    )
    return HistoricalDataResult(request=request, candles=tuple(candles))
