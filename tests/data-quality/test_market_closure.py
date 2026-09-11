from datetime import datetime, time
from zoneinfo import ZoneInfo

from packages.instruments.trading_calendar import is_market_session, is_trading_day

IST = ZoneInfo("Asia/Kolkata")


def test_weekend_is_not_a_trading_day():
    assert not is_trading_day(datetime(2026, 1, 10, tzinfo=IST).date())


def test_market_session_boundaries_are_inclusive():
    assert is_market_session(datetime(2026, 1, 5, 9, 15, tzinfo=IST))
    assert is_market_session(datetime(2026, 1, 5, 15, 30, tzinfo=IST))


def test_pre_open_and_post_close_are_closed():
    assert not is_market_session(datetime(2026, 1, 5, 9, 14, 59, tzinfo=IST))
    assert not is_market_session(datetime(2026, 1, 5, 15, 30, 1, tzinfo=IST))


def test_market_session_uses_aware_timestamp_conversion():
    utc = ZoneInfo("UTC")
    assert is_market_session(datetime(2026, 1, 5, 3, 45, tzinfo=utc))
