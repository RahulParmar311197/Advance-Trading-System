from __future__ import annotations
from .models import Candle
from .normalization import normalize_ohlcv
from .provider import MarketDataProvider
from .validation import validate_ohlcv

def ingest_ohlcv(provider: MarketDataProvider, symbol, timeframe, start, end) -> list[Candle]:
    candles = normalize_ohlcv(provider.historical_ohlcv(symbol, timeframe, start, end))
    validate_ohlcv(candles)
    return candles
