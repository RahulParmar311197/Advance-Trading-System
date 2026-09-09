from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ai_agent.backtest import BacktestRequest, BacktestResult, run_backtest_tool
from packages.market_data.models import Candle


@dataclass(frozen=True, slots=True)
class StrategyComparisonRequest:
    """Explicit reproducible configuration for comparing registered strategies."""

    strategies: tuple[str, ...]
    capital: Decimal = Decimal("100000")
    risk_per_trade: Decimal = Decimal("0.005")
    slippage_bps: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.strategies or any(not name.strip() for name in self.strategies):
            raise ValueError("strategies must contain non-empty names")
        if len(set(self.strategies)) != len(self.strategies):
            raise ValueError("strategies must not contain duplicates")
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if self.risk_per_trade <= 0 or self.risk_per_trade > 1:
            raise ValueError("risk_per_trade must be in (0, 1]")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")


@dataclass(frozen=True, slots=True)
class StrategyComparisonRow:
    """One deterministic strategy result with ranking metrics."""

    strategy_name: str
    result: BacktestResult


@dataclass(frozen=True, slots=True)
class StrategyComparisonResult:
    """Strategies ranked by total return descending, then drawdown ascending."""

    request: StrategyComparisonRequest
    rows: tuple[StrategyComparisonRow, ...]


def compare_strategies(
    candles: Sequence[Candle], request: StrategyComparisonRequest
) -> StrategyComparisonResult:
    """Run each explicitly registered strategy over identical supplied candles."""
    ordered = tuple(candles)
    _validate_candles(ordered)
    rows = [
        StrategyComparisonRow(
            strategy_name=name,
            result=run_backtest_tool(
                ordered,
                BacktestRequest(
                    strategy_name=name,
                    capital=request.capital,
                    risk_per_trade=request.risk_per_trade,
                    slippage_bps=request.slippage_bps,
                ),
            ),
        )
        for name in request.strategies
    ]
    rows.sort(
        key=lambda row: (
            -Decimal(row.result.metrics["total_return"]),
            Decimal(row.result.metrics["max_drawdown"]),
            row.strategy_name,
        )
    )
    return StrategyComparisonResult(request=request, rows=tuple(rows))


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
