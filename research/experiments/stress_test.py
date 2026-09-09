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
class StressScenario:
    name: str
    slippage_bps: Decimal
    risk_per_trade: Decimal


@dataclass(frozen=True, slots=True)
class StressScenarioResult:
    scenario: StressScenario
    trades: list[Trade]
    metrics: dict[str, Any]
    starting_equity: Decimal
    ending_equity: Decimal


def run_stress_test(
    candles: list[Candle],
    strategy: Strategy,
    scenarios: list[StressScenario],
    initial_capital: Decimal = Decimal("100000"),
) -> list[StressScenarioResult]:
    """Run the same deterministic strategy across explicitly supplied cost/risk scenarios."""
    if not candles:
        raise ValueError("candles must not be empty")
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    if not scenarios:
        raise ValueError("scenarios must not be empty")

    signals = strategy.signals(candles)
    results: list[StressScenarioResult] = []
    for scenario in scenarios:
        if scenario.slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")
        if scenario.risk_per_trade <= 0 or scenario.risk_per_trade > 1:
            raise ValueError("risk_per_trade must be greater than 0 and at most 1")
        trades = run_backtest(
            candles,
            signals,
            capital=initial_capital,
            risk_per_trade=scenario.risk_per_trade,
            slippage_bps=scenario.slippage_bps,
        )
        ending_equity = initial_capital + sum(
            (trade.net_pnl for trade in trades), Decimal(0)
        )
        results.append(
            StressScenarioResult(
                scenario=scenario,
                trades=trades,
                metrics=summarize(trades, initial_capital),
                starting_equity=initial_capital,
                ending_equity=ending_equity,
            )
        )
    return results
