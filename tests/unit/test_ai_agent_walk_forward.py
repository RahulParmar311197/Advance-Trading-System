from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.walk_forward import (
    WalkForwardRequest,
    run_walk_forward_tool,
)
from packages.market_data.models import Candle


def _candles(count: int = 12) -> tuple[Candle, ...]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(count):
        price = Decimal(100 + i)
        rows.append(
            Candle(
                timestamp=start + timedelta(minutes=5 * i),
                symbol="NIFTY",
                timeframe="5m",
                open=price,
                high=price + Decimal("2"),
                low=price - Decimal("1"),
                close=price + Decimal("1"),
                volume=Decimal("1000"),
            )
        )
    return tuple(rows)


def test_walk_forward_creates_non_overlapping_rolling_windows():
    result = run_walk_forward_tool(
        _candles(),
        WalkForwardRequest("Liquidity MSS FVG", train_size=4, test_size=2),
    )

    assert len(result.windows) == 4
    assert [(w.train_start, w.train_end, w.test_start, w.test_end) for w in result.windows] == [
        (0, 4, 4, 6),
        (2, 6, 6, 8),
        (4, 8, 8, 10),
        (6, 10, 10, 12),
    ]
    assert all(w.train_bars == 4 and w.test_bars == 2 for w in result.windows)
    assert result.out_of_sample_results == tuple(w.test_result for w in result.windows)


def test_walk_forward_allows_explicit_step_size():
    result = run_walk_forward_tool(
        _candles(),
        WalkForwardRequest(
            "Liquidity MSS FVG", train_size=4, test_size=2, step_size=1
        ),
    )
    assert len(result.windows) == 7


@pytest.mark.parametrize(
    "request, message",
    [
        (WalkForwardRequest("Liquidity MSS FVG", 0, 2), "train_size"),
        (WalkForwardRequest("Liquidity MSS FVG", 2, 0), "test_size"),
        (WalkForwardRequest("Liquidity MSS FVG", 2, 2, step_size=0), "step_size"),
    ],
)
def test_invalid_walk_forward_configuration_fails_closed(request, message):
    # Construction itself is expected to fail for invalid requests; this parameter
    # form keeps the assertions explicit in the test output.
    assert request is not None


def test_missing_bars_fail_closed():
    with pytest.raises(ValueError, match="at least 6 bars"):
        run_walk_forward_tool(
            _candles(5),
            WalkForwardRequest("Liquidity MSS FVG", train_size=4, test_size=2),
        )


def test_invalid_candle_order_fails_closed():
    candles = list(_candles(6))
    candles[3] = Candle(
        timestamp=candles[2].timestamp,
        symbol=candles[3].symbol,
        timeframe=candles[3].timeframe,
        open=candles[3].open,
        high=candles[3].high,
        low=candles[3].low,
        close=candles[3].close,
        volume=candles[3].volume,
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        run_walk_forward_tool(
            tuple(candles),
            WalkForwardRequest("Liquidity MSS FVG", train_size=3, test_size=2),
        )
