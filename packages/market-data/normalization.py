from __future__ import annotations
from decimal import Decimal
from .models import Candle
from .schemas import RawOHLCV

def normalize_ohlcv(rows: list[RawOHLCV]) -> list[Candle]:
    ordered = sorted(rows, key=lambda r: r.timestamp)
    return [Candle(r.timestamp, r.symbol.upper(), r.timeframe.lower(), Decimal(r.open), Decimal(r.high), Decimal(r.low), Decimal(r.close), Decimal(r.volume)) for r in ordered]
