from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from packages.microstructure.trade_flow import TradePrint


def trade_count(trades: Iterable[TradePrint]) -> int:
    """Return the number of supplied executed trades."""
    return sum(1 for _ in trades)


def trade_intensity(
    trades: Iterable[TradePrint], start: datetime, end: datetime
) -> Decimal:
    """Return executed-trade count per unit of elapsed time.

    TradePrint intentionally contains no timestamp, so callers supply the
    observation window explicitly. This avoids inventing timing information.
    The returned rate is trades per second.
    """
    if end <= start:
        raise ValueError("end must be after start")
    count = trade_count(trades)
    elapsed_seconds = Decimal(str((end - start).total_seconds()))
    return Decimal(count) / elapsed_seconds
