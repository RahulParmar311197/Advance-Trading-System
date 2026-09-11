from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from collections.abc import Collection, Callable

TradingDayPredicate = Callable[[date], bool]


@dataclass(frozen=True, slots=True)
class WeeklyExpiryRule:
    """Describe a weekly expiry schedule without embedding exchange-specific assumptions.

    ``weekday`` follows ``date.weekday()``: Monday is 0 and Sunday is 6.
    ``holidays`` contains dates on which the nominal expiry is not a trading day.
    If the nominal expiry is unavailable, ``adjustment`` determines how it is
    moved to another trading day.
    """

    weekday: int
    holidays: frozenset[date] = frozenset()
    adjustment: str = "previous"

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise ValueError("weekday must be between 0 (Monday) and 6 (Sunday)")
        if self.adjustment not in {"previous", "next"}:
            raise ValueError("adjustment must be 'previous' or 'next'")

    def nominal_expiry(self, reference: date) -> date:
        """Return the scheduled weekday on or after ``reference``."""
        days = (self.weekday - reference.weekday()) % 7
        return reference + timedelta(days=days)

    def expiry_on_or_after(
        self,
        reference: date,
        *,
        is_trading_day: TradingDayPredicate,
    ) -> date:
        """Return the first valid expiry on/after ``reference``.

        A nominal expiry is valid only when it is both a trading day and not in
        the configured holiday set. If it is unavailable, the configured
        adjustment is applied by searching one calendar day at a time.
        """
        nominal = self.nominal_expiry(reference)
        if self._is_valid(nominal, is_trading_day):
            return nominal

        step = -1 if self.adjustment == "previous" else 1
        candidate = nominal
        for _ in range(7):
            candidate += timedelta(days=step)
            if self._is_valid(candidate, is_trading_day):
                return candidate
        raise ValueError("no valid expiry found within one calendar week")

    def _is_valid(self, value: date, is_trading_day: TradingDayPredicate) -> bool:
        return value not in self.holidays and is_trading_day(value)


def expiry_dates(
    start: date,
    end: date,
    rule: WeeklyExpiryRule,
    *,
    is_trading_day: TradingDayPredicate,
) -> tuple[date, ...]:
    """Generate unique adjusted expiries in the inclusive ``[start, end]`` range."""
    if end < start:
        raise ValueError("end must be on or after start")

    result: list[date] = []
    reference = start
    while reference <= end:
        expiry = rule.expiry_on_or_after(reference, is_trading_day=is_trading_day)
        if expiry > end:
            break
        if not result or result[-1] != expiry:
            result.append(expiry)
        reference = expiry + timedelta(days=1)
    return tuple(result)
