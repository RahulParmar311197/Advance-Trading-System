from datetime import datetime, timezone

import pytest

from packages.options.expiry import OptionExpiryCalendar


def ts(day: int) -> datetime:
    return datetime(2026, 9, day, 10, tzinfo=timezone.utc)


def test_calendar_accepts_explicit_sorted_provider_expiries() -> None:
    calendar = OptionExpiryCalendar.from_expiries((ts(10), ts(17), ts(24)))

    assert calendar.next_on_or_after(ts(17)) == ts(17)
    assert calendar.between(ts(10), ts(24)) == (ts(10), ts(17))


def test_calendar_does_not_infer_or_deduplicate_expiries() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        OptionExpiryCalendar.from_expiries((ts(10), ts(10)))

    with pytest.raises(ValueError, match="sorted"):
        OptionExpiryCalendar.from_expiries((ts(17), ts(10)))


def test_calendar_rejects_naive_expiries_and_queries() -> None:
    naive = datetime(2026, 9, 10, 10)
    with pytest.raises(ValueError, match="timezone-aware"):
        OptionExpiryCalendar((naive,))

    calendar = OptionExpiryCalendar((ts(10),))
    with pytest.raises(ValueError, match="timezone-aware"):
        calendar.next_on_or_after(naive)


def test_calendar_uses_half_open_range_and_fails_when_empty() -> None:
    calendar = OptionExpiryCalendar((ts(10), ts(17)))

    assert calendar.between(ts(10), ts(17)) == (ts(10),)
    with pytest.raises(LookupError, match="no configured option expiry"):
        calendar.next_on_or_after(ts(18))
    with pytest.raises(ValueError, match="after"):
        calendar.between(ts(17), ts(17))
