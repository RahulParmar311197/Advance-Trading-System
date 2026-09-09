from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from packages.microstructure.trade_flow import TradePrint


def signed_notional(trades: Iterable[TradePrint]) -> Decimal:
    """Return signed traded notional from explicitly labelled trade prints."""
    return sum((trade.price * trade.signed_quantity for trade in trades), Decimal("0"))


def volume_weighted_average_price(trades: Iterable[TradePrint]) -> Decimal:
    """Return VWAP of supplied executions; fail closed for zero total quantity."""
    trades_tuple = tuple(trades)
    total_quantity = sum((trade.quantity for trade in trades_tuple), Decimal("0"))
    if total_quantity == 0:
        raise ValueError("VWAP is undefined when total quantity is zero")
    total_notional = sum(
        (trade.price * trade.quantity for trade in trades_tuple), Decimal("0")
    )
    return total_notional / total_quantity


def implementation_shortfall(
    trades: Iterable[TradePrint], arrival_price: Decimal
) -> Decimal:
    """Return quantity-weighted execution price minus the supplied arrival price."""
    if arrival_price <= 0:
        raise ValueError("arrival_price must be positive")
    vwap = volume_weighted_average_price(trades)
    return vwap - arrival_price
