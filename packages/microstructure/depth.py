from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True, slots=True)
class DepthLevel:
    """One price/quantity level in a level-2 order book."""

    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity < 0:
            raise ValueError("quantity must be non-negative")


@dataclass(frozen=True, slots=True)
class OrderBookDepth:
    """Validated bid/ask depth snapshot supplied by the market-data layer."""

    bids: tuple[DepthLevel, ...]
    asks: tuple[DepthLevel, ...]

    @classmethod
    def from_levels(
        cls,
        bids: Iterable[DepthLevel],
        asks: Iterable[DepthLevel],
    ) -> "OrderBookDepth":
        bid_levels = tuple(bids)
        ask_levels = tuple(asks)
        _validate_side(bid_levels, "bid", descending=True)
        _validate_side(ask_levels, "ask", descending=False)
        if bid_levels and ask_levels and bid_levels[0].price >= ask_levels[0].price:
            raise ValueError("best bid must be below best ask")
        return cls(bids=bid_levels, asks=ask_levels)

    @property
    def best_bid(self) -> DepthLevel | None:
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> DepthLevel | None:
        return self.asks[0] if self.asks else None


def total_depth(levels: Iterable[DepthLevel]) -> Decimal:
    """Return the supplied visible quantity without inferring missing levels."""
    levels_tuple = tuple(levels)
    _validate_side(levels_tuple, "depth", descending=None)
    return sum((level.quantity for level in levels_tuple), Decimal("0"))


def depth_within_ticks(levels: Iterable[DepthLevel], reference: Decimal, ticks: int) -> Decimal:
    """Sum quantity at supplied levels whose price is within an absolute tick count."""
    if reference <= 0:
        raise ValueError("reference must be positive")
    if ticks < 0:
        raise ValueError("ticks must be non-negative")
    levels_tuple = tuple(levels)
    _validate_side(levels_tuple, "depth", descending=None)
    return sum(
        (level.quantity for level in levels_tuple if abs(level.price - reference) <= ticks),
        Decimal("0"),
    )


def _validate_side(
    levels: tuple[DepthLevel, ...], side: str, descending: bool | None
) -> None:
    prices = [level.price for level in levels]
    if len(prices) != len(set(prices)):
        raise ValueError(f"duplicate {side} price level")
    if descending is True and any(a <= b for a, b in zip(prices, prices[1:])):
        raise ValueError("bid levels must be strictly descending")
    if descending is False and any(a >= b for a, b in zip(prices, prices[1:])):
        raise ValueError("ask levels must be strictly ascending")
