from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.backtest.engine import run_backtest
from packages.backtest.metrics import build_equity_curve, summarize
from packages.backtest.events import Trade
from packages.market_data.models import Candle
from packages.strategies.registry import get_strategy


@dataclass(frozen=True, slots=True)
class BacktestRequest:
    """Explicit backtest configuration over caller-supplied candles."""

    strategy_name: str
    capital: Decimal = Decimal("100000")
    risk_per_trade: Decimal = Decimal("0.005")
    slippage_bps: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.strategy_name.strip():
            raise ValueError("strategy_name must not be empty")
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if self.risk_per_trade <= 0 or self.risk_per_trade > 1:
            raise ValueError("risk_per_trade must be in (0, 1]")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Deterministic backtest output derived only from supplied candles."""

    request: BacktestRequest
    trades: tuple[Trade, ...]
    metrics: dict[str, Decimal | int | None]
    equity_curve: tuple[tuple[int, Decimal], ...]


def run_backtest_tool(
    candles: Sequence[Candle], request: BacktestRequest
) -> BacktestResult:
    """Run a registered strategy through the existing cost/slippage-aware engine."""
    ordered = tuple(candles)
    _validate_candles(ordered)
    strategy = get_strategy(request.strategy_name)
    candle_list = list(ordered)
    signals = strategy.signals(candle_list)
    trades = tuple(
        run_backtest(
            candle_list,
            signals,
            capital=request.capital,
            risk_per_trade=request.risk_per_trade,
            slippage_bps=request.slippage_bps,
        )
    )
    metrics = summarize(list(trades), request.capital)
    equity_curve = tuple(
        (point[0], point["equity"])
        for point in build_equity_curve(list(trades), request.capital)
    )
    return BacktestResult(
        request=request,
        trades=trades,
        metrics=metrics,
        equity_curve=equity_curve,
    )


def _validate_candles(candles: tuple[Candle, ...]) -> None:
    if not candles:
        raise ValueError("candles must not be empty")
    for previous, current in zip(candles, candles[1:]):
        if current.timestamp <= previous.timestamp:
            raise ValueError("candles must be strictly increasing by timestamp")
        if current.symbol != previous.symbol or current.timeframe != previous.timeframe:
            raise ValueError("candles must share symbol and timeframe")
    for candle in candles:
        if candle.high < candle.low:
            raise ValueError("candle high must be >= low")
        if candle.open < candle.low or candle.open > candle.high:
            raise ValueError("candle open must be within high/low")
        if candle.close < candle.low or candle.close > candle.high:
            raise ValueError("candle close must be within high/low")
        if candle.volume < 0:
            raise ValueError("candle volume must be non-negative")
