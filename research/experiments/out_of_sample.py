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
class OutOfSampleResult:
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    trades: list[Trade]
    metrics: dict[str, Any]
    starting_equity: Decimal
    ending_equity: Decimal


def run_out_of_sample(
    candles: list[Candle],
    strategy: Strategy,
    test_size: int,
    initial_capital: Decimal = Decimal("100000"),
    risk_per_trade: Decimal = Decimal("0.005"),
    slippage_bps: Decimal = Decimal("1"),
) -> OutOfSampleResult:
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    if test_size < 1:
        raise ValueError("test_size must be positive")
    if len(candles) <= test_size:
        raise ValueError("not enough candles for a non-empty train and test period")

    test_start = len(candles) - test_size
    train = candles[:test_start]
    test = candles[test_start:]

    fit = getattr(strategy, "fit", None)
    fitted = strategy if fit is None else fit(train)
    if not isinstance(fitted, Strategy):
        raise TypeError("strategy.fit(train) must return a Strategy")

    context = candles
    signals = fitted.signals(context)
    test_signals = [
        Signal(
            index=signal.index - test_start,
            direction=signal.direction,
            entry=signal.entry,
            stop=signal.stop,
            target=signal.target,
        )
        for signal in signals
        if test_start <= signal.index < len(candles)
    ]

    trades = run_backtest(
        test,
        test_signals,
        capital=initial_capital,
        risk_per_trade=risk_per_trade,
        slippage_bps=slippage_bps,
    )
    ending_equity = initial_capital + sum(
        (trade.net_pnl for trade in trades), Decimal(0)
    )
    return OutOfSampleResult(
        train_start=0,
        train_end=test_start,
        test_start=test_start,
        test_end=len(candles),
        trades=trades,
        metrics=summarize(trades, initial_capital),
        starting_equity=initial_capital,
        ending_equity=ending_equity,
    )
