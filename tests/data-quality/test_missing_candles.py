from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from packages.market_data.models import Candle
from packages.market_data.validation import find_missing_candles

IST = ZoneInfo("Asia/Kolkata")


def candle(timestamp: datetime) -> Candle:
    return Candle(
        timestamp,
        "NIFTY",
        "5m",
        Decimal("100"),
        Decimal("105"),
        Decimal("95"),
        Decimal("102"),
        Decimal("1000"),
    )


def test_detects_missing_intraday_candle():
    candles = [
        candle(datetime(2026, 1, 5, 9, 15, tzinfo=IST)),
        candle(datetime(2026, 1, 5, 9, 25, tzinfo=IST)),
    ]
    assert find_missing_candles(candles, "5m") == (
        datetime(2026, 1, 5, 9, 20, tzinfo=IST),
    )


def test_does_not_report_overnight_or_weekend_gap():
    candles = [
        candle(datetime(2026, 1, 9, 15, 25, tzinfo=IST)),
        candle(datetime(2026, 1, 12, 9, 15, tzinfo=IST)),
    ]
    assert find_missing_candles(candles, "5m") == ()


def test_rejects_unsupported_timeframe():
    candles = [candle(datetime(2026, 1, 5, 9, 15, tzinfo=IST))]
    with pytest.raises(ValueError, match="unsupported timeframe"):
        find_missing_candles(candles, "tick")
