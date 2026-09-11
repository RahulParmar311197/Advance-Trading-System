from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from packages.execution.broker import OrderRequest, OrderSide, OrderType
from packages.market_data.models import Candle


@dataclass(frozen=True, slots=True)
class SimulatedFill:
    """Deterministic fill produced from one explicitly supplied candle."""

    symbol: str
    price: Decimal
    timestamp: object


@dataclass(frozen=True, slots=True)
class ExecutionObservation:
    """Validated candle observation used by the execution simulator."""

    candle: Candle

    def __post_init__(self) -> None:
        if not self.candle.symbol.strip():
            raise ValueError("candle symbol must not be empty")
        if self.candle.open <= 0 or self.candle.high <= 0 or self.candle.low <= 0 or self.candle.close <= 0:
            raise ValueError("candle prices must be positive")
        if self.candle.high < max(self.candle.open, self.candle.close):
            raise ValueError("candle high must contain open and close")
        if self.candle.low > min(self.candle.open, self.candle.close):
            raise ValueError("candle low must contain open and close")
        if self.candle.timestamp.tzinfo is None:
            raise ValueError("candle timestamp must be timezone-aware")


def simulate_fill(
    request: OrderRequest,
    observation: ExecutionObservation,
    *,
    slippage_bps: Decimal = Decimal("0"),
) -> SimulatedFill | None:
    """Simulate one order against one supplied OHLC observation.

    This is an execution model, not a market-data source: it creates no
    observations and never assumes liquidity beyond the supplied candle.
    Market orders execute at the candle open. Limit orders execute at their
    limit when the candle crosses that level. Stop orders execute at the stop
    unless the candle opens beyond the stop, in which case the supplied open
    is used to model a gap. Slippage is applied only to market/stop executions;
    limit orders remain at their contractual limit price.
    """
    if slippage_bps < 0:
        raise ValueError("slippage_bps must be non-negative")
    candle = observation.candle
    if candle.symbol != request.symbol:
        raise ValueError("candle symbol does not match order symbol")

    price: Decimal | None
    apply_slippage = False
    if request.order_type is OrderType.MARKET:
        price = candle.open
        apply_slippage = True
    elif request.order_type is OrderType.LIMIT:
        assert request.limit_price is not None
        if request.side is OrderSide.BUY and candle.low <= request.limit_price:
            price = request.limit_price
        elif request.side is OrderSide.SELL and candle.high >= request.limit_price:
            price = request.limit_price
        else:
            price = None
    else:
        assert request.stop_price is not None
        if request.side is OrderSide.BUY and candle.high >= request.stop_price:
            price = max(candle.open, request.stop_price)
            apply_slippage = True
        elif request.side is OrderSide.SELL and candle.low <= request.stop_price:
            price = min(candle.open, request.stop_price)
            apply_slippage = True
        else:
            price = None

    if price is None:
        return None
    if apply_slippage and slippage_bps:
        factor = Decimal("1") + slippage_bps / Decimal("10000")
        if request.side is OrderSide.SELL:
            factor = Decimal("1") - slippage_bps / Decimal("10000")
        price *= factor
    return SimulatedFill(symbol=candle.symbol, price=price, timestamp=candle.timestamp)
