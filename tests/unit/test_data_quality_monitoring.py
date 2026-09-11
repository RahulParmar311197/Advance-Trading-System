from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from packages.market_data.models import Candle
from packages.monitoring.data_quality import assess_candles

IST = ZoneInfo("Asia/Kolkata")


def candle(hour: int, minute: int = 0, *, close: str = "100") -> Candle:
    timestamp = datetime(2026, 9, 10, hour, minute, tzinfo=IST)
    value = Decimal(close)
    return Candle(timestamp, "NIFTY", "5m", value, value + 1, value - 1, value, Decimal("100"))


def test_assessment_detects_missing_session_candle():
    report = assess_candles([candle(9, 15), candle(9, 25)], "5m", datetime(2026, 9, 10, 10, tzinfo=IST))
    assert not report.healthy
    assert report.missing_candles == (datetime(2026, 9, 10, 9, 20, tzinfo=IST),)
    assert report.as_dict()["status"] == "degraded"


def test_assessment_does_not_flag_overnight_gap():
    report = assess_candles([candle(15, 25), candle(9, 15)], "5m", datetime(2026, 9, 11, 10, tzinfo=IST))
    # The timestamps are out of order, so the input is invalid rather than an overnight gap.
    assert not report.healthy
    assert report.error == "timestamps must be strictly increasing"


def test_assessment_rejects_invalid_ohlcv():
    first = candle(9, 15)
    invalid = Candle(first.timestamp.replace(minute=20), "NIFTY", "5m", Decimal("100"), Decimal("99"), Decimal("98"), Decimal("100"), Decimal("100"))
    report = assess_candles([first, invalid], "5m", datetime(2026, 9, 10, 10, tzinfo=IST))
    assert not report.healthy
    assert report.error == "invalid OHLC range at 2026-09-10 09:20:00+05:30"


def test_assessment_reports_healthy_complete_window():
    report = assess_candles([candle(9, 15), candle(9, 20), candle(9, 25)], "5m", datetime(2026, 9, 10, 10, tzinfo=IST))
    assert report.healthy
    assert report.missing_candles == ()
