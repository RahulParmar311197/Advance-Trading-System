from datetime import date

import pytest

from packages.instruments.expiry import WeeklyExpiryRule, expiry_dates


def weekdays_only(day: date) -> bool:
    return day.weekday() < 5


def test_weekly_expiry_uses_configured_weekday() -> None:
    rule = WeeklyExpiryRule(weekday=1)

    assert rule.nominal_expiry(date(2026, 9, 14)) == date(2026, 9, 15)


def test_holiday_moves_expiry_to_previous_trading_day() -> None:
    rule = WeeklyExpiryRule(
        weekday=1,
        holidays=frozenset({date(2026, 9, 15)}),
        adjustment="previous",
    )

    assert rule.expiry_on_or_after(date(2026, 9, 14), is_trading_day=weekdays_only) == date(2026, 9, 14)


def test_holiday_can_move_expiry_to_next_trading_day() -> None:
    rule = WeeklyExpiryRule(
        weekday=1,
        holidays=frozenset({date(2026, 9, 15)}),
        adjustment="next",
    )

    assert rule.expiry_on_or_after(date(2026, 9, 14), is_trading_day=weekdays_only) == date(2026, 9, 16)


def test_expiry_dates_are_inclusive_and_adjusted() -> None:
    rule = WeeklyExpiryRule(
        weekday=1,
        holidays=frozenset({date(2026, 9, 15)}),
    )

    assert expiry_dates(
        date(2026, 9, 1),
        date(2026, 9, 30),
        rule,
        is_trading_day=weekdays_only,
    ) == (date(2026, 9, 14), date(2026, 9, 22), date(2026, 9, 29))


def test_invalid_rule_and_range_fail_closed() -> None:
    with pytest.raises(ValueError, match="weekday"):
        WeeklyExpiryRule(weekday=7)
    with pytest.raises(ValueError, match="adjustment"):
        WeeklyExpiryRule(weekday=1, adjustment="nearest")
    with pytest.raises(ValueError, match="end"):
        expiry_dates(date(2026, 9, 2), date(2026, 9, 1), WeeklyExpiryRule(1), is_trading_day=weekdays_only)
