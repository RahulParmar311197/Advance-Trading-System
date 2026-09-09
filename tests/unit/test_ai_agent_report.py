from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.report import generate_report
from packages.ai_agent.strategy_comparison import StrategyComparisonRequest, compare_strategies
from packages.market_data.models import Candle


def _candles() -> tuple[Candle, ...]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return tuple(
        Candle(
            start + timedelta(minutes=5 * i),
            "NIFTY",
            "5m",
            Decimal(100 + i),
            Decimal(102 + i),
            Decimal(99 + i),
            Decimal(101 + i),
            Decimal("1000"),
        )
        for i in range(12)
    )


def test_report_is_factual_and_deterministic():
    comparison = compare_strategies(
        _candles(), StrategyComparisonRequest(("Liquidity MSS FVG",))
    )
    first = generate_report(comparison)
    second = generate_report(comparison)

    assert first == second
    markdown = first.as_markdown()
    assert "Liquidity MSS FVG" in markdown
    assert "Top-ranked total return" in markdown
    assert "not a claim of future performance" in markdown


def test_report_rejects_empty_comparison():
    class EmptyComparison:
        rows = ()

    with pytest.raises(ValueError, match="at least one"):
        generate_report(EmptyComparison())
