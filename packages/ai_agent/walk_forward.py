from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.market_data.models import Candle
from packages.ai_agent.backtest import BacktestRequest, BacktestResult, run_backtest_tool


@dataclass(frozen=True, slots=True)
class WalkForwardRequest:
    """Rolling in-sample/out-of-sample evaluation configuration."""

    strategy_name: str
    train_size: int
    test_size: int
    step_size: int | None = None
    capital: Decimal = Decimal("100000")
    risk_per_trade: Decimal = Decimal("0.005")
    slippage_bps: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.strategy_name.strip():
            raise ValueError("strategy_name must not be empty")
        if self.train_size <= 0:
            raise ValueError("train_size must be positive")
        if self.test_size <= 0:
            raise ValueError("test_size must be positive")
        step = self.step_size if self.step_size is not None else self.test_size
        if step <= 0:
            raise ValueError("step_size must be positive")
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if self.risk_per_trade <= 0 or self.risk_per_trade > 1:
            raise ValueError("risk_per_trade must be in (0, 1]")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")

    @property
    def resolved_step_size(self) -> int:
        return self.step_size if self.step_size is not None else self.test_size


@dataclass(frozen=True, slots=True)
class WalkForwardWindow:
    """One train/test window; training is reported, OOS is executed."""

    index: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    train_bars: int
    test_bars: int
    train_result: BacktestResult
    test_result: BacktestResult


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    """Deterministic walk-forward result over caller-supplied candles."""

    request: WalkForwardRequest
    windows: tuple[WalkForwardWindow, ...]

    @property
    def out_of_sample_results(self) -> tuple[BacktestResult, ...]:
        return tuple(window.test_result for window in self.windows)


def run_walk_forward_tool(
    candles: Sequence[Candle], request: WalkForwardRequest
) -> WalkForwardResult:
    """Run rolling train/test windows using the existing backtest tool."""
    ordered = tuple(candles)
    _validate_candles(ordered)
    minimum = request.train_size + request.test_size
    if len(ordered) < minimum:
        raise ValueError(
            f"candles require at least {minimum} bars for the requested windows"
        )

    windows: list[WalkForwardWindow] = []
    start = 0
    index = 0
    while start + minimum <= len(ordered):
        train_end = start + request.train_size
        test_end = train_end + request.test_size
        train_candles = ordered[start:train_end]
        test_candles = ordered[train_end:test_end]

        train_result = run_backtest_tool(
            train_candles,
            BacktestRequest(
                strategy_name=request.strategy_name,
                capital=request.capital,
                risk_per_trade=request.risk_per_trade,
                slippage_bps=request.slippage_bps,
            ),
        )
        test_result = run_backtest_tool(
            test_candles,
            BacktestRequest(
                strategy_name=request.strategy_name,
                capital=request.capital,
                risk_per_trade=request.risk_per_trade,
                slippage_bps=request.slippage_bps,
            ),
        )
        windows.append(
            WalkForwardWindow(
                index=index,
                train_start=start,
                train_end=train_end,
                test_start=train_end,
                test_end=test_end,
                train_bars=len(train_candles),
                test_bars=len(test_candles),
                train_result=train_result,
                test_result=test_result,
            )
        )
        index += 1
        start += request.resolved_step_size

    if not windows:
        raise ValueError("no complete walk-forward window available")
    return WalkForwardResult(request=request, windows=tuple(windows))


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
