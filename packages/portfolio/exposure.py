from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable


def aggregate_exposure(positions: Iterable[dict[str, object]]) -> dict[str, Decimal]:
    """Aggregate absolute notional exposure by symbol from open positions."""
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for position in positions:
        symbol = str(position.get("symbol", "")).strip()
        if not symbol:
            raise ValueError("position symbol is required")
        quantity = Decimal(str(position.get("quantity", "0")))
        price = Decimal(str(position.get("price", "0")))
        if quantity < 0 or price < 0:
            raise ValueError("position quantity and price must be non-negative")
        totals[symbol] += quantity * price
    return dict(totals)


def total_exposure(positions: Iterable[dict[str, object]]) -> Decimal:
    return sum(aggregate_exposure(positions).values(), Decimal("0"))
