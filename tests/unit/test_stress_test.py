from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.stress_test import StressScenario, run_stress_test


class FixedTargetStrategy(Strategy):
    def signals(self, candles):
        return [Signal(index=0, direction="bullish", entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102"))]


def candles() -> list[Candle]:
    base = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    return [
        Candle(base, "NIFTY", "5m", Decimal("100"), Decimal("100"), Decimal("99"), Decimal("100"), Decimal("1000")),
        Candle(base + timedelta(minutes=5), "NIFTY", "5m", Decimal("100"), Decimal("102"), Decimal("100"), Decimal("102"), Decimal("1000")),
    ]


def test_stress_test_runs_same_strategy_under_multiple_scenarios():
    results = run_stress_test(candles(), FixedTargetStrategy(), [
        StressScenario("base", Decimal("0"), Decimal("0.005")),
        StressScenario("high_slippage", Decimal("100"), Decimal("0.005")),
    ])
    assert [r.scenario.name for r in results] == ["base", "high_slippage"]
    assert all(len(r.trades) == 1 for r in results)
    assert results[0].ending_equity > results[1].ending_equity
    assert results[0].metrics["total_return"] > results[1].metrics["total_return"]


def test_stress_test_rejects_invalid_scenarios():
    try:
        run_stress_test(candles(), FixedTargetStrategy(), [StressScenario("invalid", Decimal("0"), Decimal("1.1"))])
    except ValueError as exc:
        assert "risk_per_trade" in str(exc)
    else:
        raise AssertionError("invalid stress scenario was accepted")
