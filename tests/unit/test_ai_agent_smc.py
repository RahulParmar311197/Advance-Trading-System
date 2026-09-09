from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.smc import SMCRequest, detect_smc
from packages.market_data.models import Candle


def _candles() -> list[Candle]:
    start = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    values = [
        (100, 102, 99, 101),
        (101, 104, 100, 103),
        (103, 105, 101, 102),
        (102, 108, 100, 107),
        (107, 109, 104, 105),
        (105, 112, 103, 111),
        (111, 113, 108, 109),
        (109, 115, 107, 114),
        (114, 116, 111, 113),
    ]
    return [
        Candle(
            start + timedelta(minutes=5 * i),
            "NIFTY",
            "5m",
            Decimal(open_),
            Decimal(high),
            Decimal(low),
            Decimal(close),
            Decimal("1000"),
        )
        for i, (open_, high, low, close) in enumerate(values)
    ]


def test_detect_smc_runs_existing_deterministic_pipeline() -> None:
    result = detect_smc(_candles(), SMCRequest(swing_left=1, swing_right=1))

    assert result.swings
    assert result.events
    assert {event.event for event in result.events} <= {
        "bos",
        "mss",
        "liquidity_sweep",
        "fvg",
    }
    assert all(event.symbol == "NIFTY" for event in result.events)
    assert all(event.timeframe == "5m" for event in result.events)
    assert all(event.confidence is None for event in result.events)


def test_detect_smc_is_deterministic() -> None:
    request = SMCRequest(swing_left=1, swing_right=1)

    assert detect_smc(_candles(), request) == detect_smc(_candles(), request)


def test_detect_smc_fails_closed_for_empty_or_mixed_candles() -> None:
    with pytest.raises(ValueError, match="candles must not be empty"):
        detect_smc([])

    candles = _candles()
    candles[-1] = Candle(
        candles[-1].timestamp,
        "BANKNIFTY",
        "5m",
        candles[-1].open,
        candles[-1].high,
        candles[-1].low,
        candles[-1].close,
        candles[-1].volume,
    )
    with pytest.raises(ValueError, match="share symbol and timeframe"):
        detect_smc(candles)


def test_smc_request_validates_swing_parameters() -> None:
    with pytest.raises(ValueError, match="swing_left"):
        SMCRequest(swing_left=0)
    with pytest.raises(ValueError, match="swing_right"):
        SMCRequest(swing_right=0)
