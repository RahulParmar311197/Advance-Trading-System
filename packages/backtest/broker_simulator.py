from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from packages.backtest.commission import commission
from packages.backtest.slippage import apply_slippage


@dataclass(frozen=True, slots=True)
class SimulatedFill:
    side: str
    requested_price: Decimal
    filled_price: Decimal
    quantity: Decimal
    commission: Decimal


class BrokerSimulator:
    """Deterministic broker simulator for backtest order fills."""

    def __init__(self, slippage_bps: Decimal = Decimal("1")) -> None:
        if slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")
        self.slippage_bps = slippage_bps

    def fill(self, side: str, price: Decimal, quantity: Decimal) -> SimulatedFill:
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if price <= 0 or quantity <= 0:
            raise ValueError("price and quantity must be positive")
        filled_price = apply_slippage(price, side, self.slippage_bps)
        return SimulatedFill(
            side=side,
            requested_price=price,
            filled_price=filled_price,
            quantity=quantity,
            commission=commission(filled_price * quantity),
        )
