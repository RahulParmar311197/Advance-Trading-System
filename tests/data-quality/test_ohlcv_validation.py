from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.market_data.models import Candle
from packages.market_data.validation import validate_ohlcv

BASE = datetime(2026, 1, 5, 9, 15, tzinfo=timezone.utc)


def candle(
    timestamp: datetime = BASE,
    *,
    open_: str = "100",
    high: str = "105",
    low: str = "95",
    close: str = "102",
    volume: str = "1000",
) -> Candle:
    return Candle(
        timestamp,
        "NIFTY",
        "5m",
        Decimal(open_),
        Decimal(high),
        Decimal(low),
        Decimal(close),
        Decimal(volume),
    )


def test_rejects_high_below_open_or_close():
    with pytest.raises(ValueError, match="invalid OHLC range"):
        validate_ohlcv([candle(high="99")])


def test_rejects_low_above_open_or_close():
    with pytest.raises(ValueError, match="invalid OHLC range"):
        validate_ohlcv([candle(low="101")])


def test_rejects_low_above_high():
    with pytest.raises(ValueError, match="invalid OHLC range"):
        validate_ohlcv([candle(high="100", low="101")])


def test_rejects_negative_volume():
    with pytest.raises(ValueError, match="negative volume"):
        validate_ohlcv([candle(volume="-1")])


def test_rejects_duplicate_timestamps():
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_ohlcv([candle(), candle(BASE)])


def test_rejects_out_of_order_timestamps():
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_ohlcv([candle(BASE + timedelta(minutes=5)), candle(BASE)])


def test_accepts_valid_monotonic_ohlcv():
    validate_ohlcv(
        [
            candle(BASE),
            candle(BASE + timedelta(minutes=5), open_="102", high="106", low="101", close="105"),
        ]
    )
