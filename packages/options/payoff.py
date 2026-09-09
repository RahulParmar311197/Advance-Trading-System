from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class OptionLeg:
    """One long or short European option position for expiry payoff analysis."""

    strike: Decimal
    premium: Decimal
    quantity: Decimal
    right: str
    position: str

    def __post_init__(self) -> None:
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.premium < 0:
            raise ValueError("premium must be non-negative")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.right not in {"call", "put"}:
            raise ValueError("right must be call or put")
        if self.position not in {"long", "short"}:
            raise ValueError("position must be long or short")

    def payoff(self, underlying_price: Decimal) -> Decimal:
        """Return this leg's expiry P&L, including the supplied premium."""
        if underlying_price < 0:
            raise ValueError("underlying_price must be non-negative")
        intrinsic = (
            max(underlying_price - self.strike, Decimal("0"))
            if self.right == "call"
            else max(self.strike - underlying_price, Decimal("0"))
        )
        unit_pnl = intrinsic - self.premium
        if self.position == "short":
            unit_pnl = -unit_pnl
        return unit_pnl * self.quantity


def strategy_payoff(
    legs: tuple[OptionLeg, ...], underlying_price: Decimal
) -> Decimal:
    """Return aggregate expiry P&L for supplied option legs."""
    if not legs:
        raise ValueError("legs must not be empty")
    return sum((leg.payoff(underlying_price) for leg in legs), Decimal("0"))
