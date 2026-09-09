from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class BidAskQuote:
    """One level-1 bid/ask quote used for deterministic spread analytics."""

    bid: Decimal
    ask: Decimal

    def __post_init__(self) -> None:
        if self.bid < 0 or self.ask < 0:
            raise ValueError("bid and ask must be non-negative")
        if self.bid > self.ask:
            raise ValueError("bid must not exceed ask")

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")

    @property
    def relative_spread(self) -> Decimal:
        if self.mid == 0:
            raise ValueError("relative spread is undefined when mid is zero")
        return self.spread / self.mid


def bid_ask_spread(bid: Decimal, ask: Decimal) -> Decimal:
    """Return the absolute bid/ask spread for one quote."""
    return BidAskQuote(bid=bid, ask=ask).spread


def relative_bid_ask_spread(bid: Decimal, ask: Decimal) -> Decimal:
    """Return spread divided by mid price for one quote."""
    return BidAskQuote(bid=bid, ask=ask).relative_spread
