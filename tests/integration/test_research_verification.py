from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.out_of_sample import run_out_of_sample
from research.experiments.stress_test import StressScenario, run_stress_test
from research.experiments.walk_forward import run_walk_forward


def make_candles(count: int) -> list[Candle]:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            timestamp=start + timedelta(minutes=5 * index),
            symbol="NIFTY",
            timeframe="5m",
            open=Decimal(100 + index),
            high=Decimal(101 + index),
            low=Decimal(99 + index),
            close=Decimal(100 + index),
            volume=Decimal(1000),
        )
        for index in range(count)
    ]


class FirstTestCandleStrategy(Strategy):
    """Deterministic test-only strategy shared by all research evaluators."""

    def signals(self, candles: list[Candle]) -> list[Signal]:
        if len(candles) < 4:
            return []
        candle = candles[-1]
        return [
            Signal(
                index=len(candles) - 1,
                direction="bullish",
                entry=candle.close,
                stop=candle.close - Decimal("1"),
                target=candle.close + Decimal("1"),
            )
        ]


def test_research_verification_runs_oos_walk_forward_and_stress_together():
    dataset = make_candles(6)
    strategy = FirstTestCandleStrategy()

    oos = run_out_of_sample(
        dataset,
        strategy,
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )
    walk_forward = run_walk_forward(
        dataset,
        strategy,
        train_size=3,
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )
    stress = run_stress_test(
        dataset,
        strategy,
        [
            StressScenario(
                name="base",
                slippage_bps=Decimal("0"),
                risk_per_trade=Decimal("0.01"),
            ),
            StressScenario(
                name="high_slippage",
                slippage_bps=Decimal("100"),
                risk_per_trade=Decimal("0.01"),
            ),
        ],
        initial_capital=Decimal("100000"),
    )

    assert len(oos.trades) == 1
    assert len(walk_forward.trades) == 1
    assert len(walk_forward.windows) == 1
    assert [result.scenario.name for result in stress] == ["base", "high_slippage"]
    assert all(result.trades for result in stress)
    assert stress[1].ending_equity < stress[0].ending_equity
    assert oos.ending_equity > oos.starting_equity
    assert walk_forward.final_equity > Decimal("100000")
