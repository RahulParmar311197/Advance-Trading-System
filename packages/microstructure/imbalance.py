from __future__ import annotations

from decimal import Decimal


def bid_ask_imbalance(bid_quantity: Decimal, ask_quantity: Decimal) -> Decimal:
    """Return normalized level-1 order-book imbalance in [-1, 1]."""
    _validate_quantity(bid_quantity, "bid_quantity")
    _validate_quantity(ask_quantity, "ask_quantity")
    total = bid_quantity + ask_quantity
    if total == 0:
        raise ValueError("imbalance is undefined when total quantity is zero")
    return (bid_quantity - ask_quantity) / total


def depth_imbalance(
    bid_quantities: tuple[Decimal, ...], ask_quantities: tuple[Decimal, ...]
) -> Decimal:
    """Return normalized imbalance across explicitly supplied visible depth."""
    bid_total = _sum_quantities(bid_quantities, "bid_quantities")
    ask_total = _sum_quantities(ask_quantities, "ask_quantities")
    return bid_ask_imbalance(bid_total, ask_total)


def _sum_quantities(values: tuple[Decimal, ...], name: str) -> Decimal:
    total = Decimal("0")
    for value in values:
        _validate_quantity(value, name)
        total += value
    return total


def _validate_quantity(value: Decimal, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
