from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable

@dataclass(frozen=True, slots=True)
class RawOHLCV:
    timestamp: datetime
    symbol: str
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

def validate_required_columns(rows: Iterable[RawOHLCV]) -> None:
    for row in rows:
        if not row.symbol or not row.timeframe:
            raise ValueError("symbol and timeframe are required")
