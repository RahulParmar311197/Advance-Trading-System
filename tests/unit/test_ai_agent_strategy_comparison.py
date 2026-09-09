from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.strategy_comparison import (
    StrategyComparisonRequest,
    compare_strategies,
)
from packages.market_data.models import Candle


def _candles(count: int = 12) -> tuple[Candle, ...]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return tuple(
        Candle(
            timestamp=start + timedelta(minutes=5 * i),
            symbol="NIFTY",
            timeframe="5m",
            open=Decimal(100 + i),
            high=Decimal(102 + i),
            low=Decimal(99 + i),
            close=Decimal(101 + i),
            volume=Decimal("1000"),
        )
        for i in range(count)
    )


def test_strategy_comparison_is_deterministic_and_ranked():
    request = StrategyComparisonRequest(("Liquidity MSS FVG",))
    first = compare_strategies(_candles(), request)
    second = compare_strategies(_candles(), request)

    assert first == second
    assert len(first.rows) == 1
    assert first.rows[0].strategy_name == "Liquidity MSS FVG"
    assert "total_return" in first.rows[0].result.metrics


@pytest.mark.parametrize(
    "strategies,message",
    [
        ((), "strategies"),
        (("",), "strategies"),
        (("Liquidity MSS FVG", "Liquidity MSS FVG"), "duplicates"),
    ],
)
def test_invalid_strategy_comparison_request_fails_closed(strategies, message):
    with pytest.raises(ValueError, match=message):
        StrategyComparisonRequest(strategies)


def test_empty_candles_fail_closed():
    with pytest.raises(ValueError, match="candles"):
        compare_strategies((), StrategyComparisonRequest(("Liquidity MSS FVG",)))
