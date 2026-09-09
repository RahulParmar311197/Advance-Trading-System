from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from packages.microstructure.depth import OrderBookDepth

ExecutionSide = Literal["buy", "sell"]


@dataclass(frozen=True, slots=True)
class ExecutionFill:
    """One deterministic fill against a supplied visible order-book level."""

    price: Decimal
    quantity: Decimal


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Result of consuming only the visible side of a supplied order book."""

    side: ExecutionSide
    requested_quantity: Decimal
    filled_quantity: Decimal
    unfilled_quantity: Decimal
    notional: Decimal
    fills: tuple[ExecutionFill, ...]

    @property
    def average_price(self) -> Decimal | None:
        if self.filled_quantity == 0:
            return None
        return self.notional / self.filled_quantity


def execute_market_order(
    book: OrderBookDepth, side: ExecutionSide, quantity: Decimal
) -> ExecutionResult:
    """Consume visible ask/bid levels for a deterministic market-order estimate.

    No hidden liquidity, latency, queue position, or future fills are inferred.
    A partially filled result is returned when requested quantity exceeds the
    supplied visible depth.
    """
    if side not in {"buy", "sell"}:
        raise ValueError("side must be buy or sell")
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    levels = book.asks if side == "buy" else book.bids
    fills: list[ExecutionFill] = []
    remaining = quantity
    notional = Decimal("0")
    for level in levels:
        if remaining == 0:
            break
        fill_quantity = min(remaining, level.quantity)
        if fill_quantity == 0:
            continue
        fills.append(ExecutionFill(price=level.price, quantity=fill_quantity))
        notional += level.price * fill_quantity
        remaining -= fill_quantity

    filled = quantity - remaining
    return ExecutionResult(
        side=side,
        requested_quantity=quantity,
        filled_quantity=filled,
        unfilled_quantity=remaining,
        notional=notional,
        fills=tuple(fills),
    )
