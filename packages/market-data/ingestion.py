from __future__ import annotations

from datetime import datetime

from .models import Candle
from .normalization import normalize_ohlcv
from .provider import MarketDataProvider
from .repository import CandleRepository
from .validation import validate_ohlcv


def ingest_ohlcv(provider: MarketDataProvider, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]:
    raw = provider.historical_ohlcv(symbol, timeframe, start, end)
    candles = normalize_ohlcv(raw, symbol=symbol, timeframe=timeframe)
    validate_ohlcv(candles)
    return candles


def ingest_historical_ohlcv(
    provider: MarketDataProvider,
    repository: CandleRepository,
    symbol: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    data_version: str,
) -> list[Candle]:
    """Fetch, normalize, validate, and idempotently persist provider OHLCV."""
    candles = ingest_ohlcv(provider, symbol, timeframe, start, end)
    repository.save(candles, data_version=data_version)
    return candles
