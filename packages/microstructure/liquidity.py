from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from packages.microstructure.depth import OrderBookDepth, total_depth
from packages.microstructure.spread import BidAskQuote


@dataclass(frozen=True, slots=True)
class LiquiditySnapshot:
    """Deterministic liquidity view over one supplied order-book snapshot."""

    quote: BidAskQuote
    depth: OrderBookDepth

    @property
    def visible_depth(self) -> Decimal:
        """Return total visible bid plus ask quantity."""
        return total_depth(self.depth.bids) + total_depth(self.depth.asks)

    @property
    def spread(self) -> Decimal:
        """Return the absolute quoted spread."""
        return self.quote.spread

    @property
    def relative_spread(self) -> Decimal:
        """Return spread normalized by the quote midpoint."""
        return self.quote.relative_spread


def visible_liquidity(depth: OrderBookDepth) -> Decimal:
    """Return total visible quantity across the supplied bid and ask depth."""
    return total_depth(depth.bids) + total_depth(depth.asks)


def depth_recovery_ratio(
    initial_depth: Decimal,
    stressed_depth: Decimal,
    recovered_depth: Decimal,
) -> Decimal:
    """Measure the fraction of stress-induced depth depletion that recovered.

    The observations are caller-supplied snapshots. No timing or missing
    market data is inferred. Values above one are retained when recovery
    exceeds the initial depth rather than being silently capped.
    """
    _validate_non_negative(initial_depth, "initial_depth")
    _validate_non_negative(stressed_depth, "stressed_depth")
    _validate_non_negative(recovered_depth, "recovered_depth")
    if stressed_depth > initial_depth:
        raise ValueError("stressed_depth must not exceed initial_depth")
    if recovered_depth < stressed_depth:
        raise ValueError("recovered_depth must not be below stressed_depth")
    depletion = initial_depth - stressed_depth
    if depletion == 0:
        raise ValueError("depth recovery is undefined without initial depletion")
    return (recovered_depth - stressed_depth) / depletion


def spread_recovery_ratio(
    initial_spread: Decimal,
    stressed_spread: Decimal,
    recovered_spread: Decimal,
) -> Decimal:
    """Measure the fraction of stress-induced spread widening that recovered."""
    _validate_non_negative(initial_spread, "initial_spread")
    _validate_non_negative(stressed_spread, "stressed_spread")
    _validate_non_negative(recovered_spread, "recovered_spread")
    if stressed_spread < initial_spread:
        raise ValueError("stressed_spread must not be below initial_spread")
    if recovered_spread > stressed_spread:
        raise ValueError("recovered_spread must not exceed stressed_spread")
    widening = stressed_spread - initial_spread
    if widening == 0:
        raise ValueError("spread recovery is undefined without initial widening")
    return (stressed_spread - recovered_spread) / widening


def _validate_non_negative(value: Decimal, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
