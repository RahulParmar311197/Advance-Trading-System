from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True, slots=True)
class TradePrint:
    """One executed trade with an explicitly supplied aggressor side."""

    price: Decimal
    quantity: Decimal
    side: str

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity < 0:
            raise ValueError("quantity must be non-negative")
        if self.side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")

    @property
    def signed_quantity(self) -> Decimal:
        return self.quantity if self.side == "buy" else -self.quantity


def signed_trade_volume(trades: Iterable[TradePrint]) -> Decimal:
    """Return signed executed quantity using only explicit trade-side labels."""
    return sum((trade.signed_quantity for trade in trades), Decimal("0"))


def trade_flow_imbalance(trades: Iterable[TradePrint]) -> Decimal:
    """Return normalized buy-minus-sell executed-volume imbalance."""
    trades_tuple = tuple(trades)
    buy_volume = sum(
        (trade.quantity for trade in trades_tuple if trade.side == "buy"),
        Decimal("0"),
    )
    sell_volume = sum(
        (trade.quantity for trade in trades_tuple if trade.side == "sell"),
        Decimal("0"),
    )
    total = buy_volume + sell_volume
    if total == 0:
        raise ValueError("trade flow imbalance is undefined when total quantity is zero")
    return (buy_volume - sell_volume) / total
