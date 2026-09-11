from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.backtest.engine import run_backtest
from packages.backtest.events import Trade
from packages.backtest.metrics import summarize
from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy


@dataclass(frozen=True, slots=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    windows: list[dict[str, Any]]
    trades: list[Trade]
    final_equity: Decimal


def make_windows(
    candle_count: int,
    train_size: int,
    test_size: int,
    step: int | None = None,
) -> list[WalkForwardWindow]:
    if candle_count < 1:
        raise ValueError("candle_count must be positive")
    if train_size < 1 or test_size < 1:
        raise ValueError("train_size and test_size must be positive")
    step = test_size if step is None else step
    if step < 1:
        raise ValueError("step must be positive")

    windows: list[WalkForwardWindow] = []
    test_start = train_size
    while test_start + test_size <= candle_count:
        windows.append(
            WalkForwardWindow(
                train_start=test_start - train_size,
                train_end=test_start,
                test_start=test_start,
                test_end=test_start + test_size,
            )
        )
        test_start += step
    return windows


def _fit_strategy(strategy: Strategy, train: list[Candle]) -> Strategy:
    fit = getattr(strategy, "fit", None)
    if fit is None:
        return strategy
    fitted = fit(train)
    if not isinstance(fitted, Strategy):
        raise TypeError("strategy.fit(train) must return a Strategy")
    return fitted


def _oos_signals(
    strategy: Strategy,
    candles: list[Candle],
    train_start: int,
    test_start: int,
    test_end: int,
) -> list[Signal]:
    """Generate test signals causally, never exposing future test candles."""
    result: list[Signal] = []
    for global_index in range(test_start, test_end):
        context = candles[train_start : global_index + 1]
        for signal in strategy.signals(context):
            relative_index = global_index - train_start
            if signal.index != relative_index:
                continue
            result.append(
                Signal(
                    index=global_index - test_start,
                    direction=signal.direction,
                    entry=signal.entry,
                    stop=signal.stop,
                    target=signal.target,
                )
            )
    return result


def run_walk_forward(
    candles: list[Candle],
    strategy: Strategy,
    train_size: int,
    test_size: int,
    initial_capital: Decimal = Decimal("100000"),
    risk_per_trade: Decimal = Decimal("0.005"),
    slippage_bps: Decimal = Decimal("1"),
    step: int | None = None,
) -> WalkForwardResult:
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    windows = make_windows(len(candles), train_size, test_size, step)
    if not windows:
        raise ValueError("not enough candles for one train/test window")

    equity = initial_capital
    all_trades: list[Trade] = []
    records: list[dict[str, Any]] = []

    for window_number, window in enumerate(windows, start=1):
        train = candles[window.train_start : window.train_end]
        test = candles[window.test_start : window.test_end]
        fitted = _fit_strategy(strategy, train)
        signals = _oos_signals(
            fitted,
            candles,
            window.train_start,
            window.test_start,
            window.test_end,
        )
        trades = run_backtest(
            test,
            signals,
            capital=equity,
            risk_per_trade=risk_per_trade,
            slippage_bps=slippage_bps,
        )
        metrics = summarize(trades, equity)
        equity = equity + sum((trade.net_pnl for trade in trades), Decimal(0))
        all_trades.extend(trades)
        records.append(
            {
                "window": window_number,
                "train_start": window.train_start,
                "train_end": window.train_end,
                "test_start": window.test_start,
                "test_end": window.test_end,
                "trade_count": len(trades),
                "starting_equity": equity - sum((trade.net_pnl for trade in trades), Decimal(0)),
                "ending_equity": equity,
                "metrics": metrics,
            }
        )

    return WalkForwardResult(windows=records, trades=all_trades, final_equity=equity)
