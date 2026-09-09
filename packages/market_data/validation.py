from __future__ import annotations
from .models import Candle

def validate_ohlcv(candles: list[Candle]) -> None:
    previous = None
    for c in candles:
        if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.low > c.high:
            raise ValueError(f"invalid OHLC range at {c.timestamp}")
        if c.volume < 0:
            raise ValueError(f"negative volume at {c.timestamp}")
        if previous is not None and c.timestamp <= previous:
            raise ValueError("timestamps must be strictly increasing")
        previous = c.timestamp
