from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

TradingDayPredicate = Callable[[date], bool]


@dataclass(frozen=True, slots=True)
class WeeklyExpiryRule:
    """Describe a weekly expiry schedule without exchange-specific assumptions."""

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

    def adjust_expiry(self, nominal: date, *, is_trading_day: TradingDayPredicate) -> date:
        """Adjust an unavailable nominal expiry to the configured trading day."""
        if self._is_valid(nominal, is_trading_day):
            return nominal

        step = -1 if self.adjustment == "previous" else 1
        candidate = nominal
        for _ in range(7):
            candidate += timedelta(days=step)
            if self._is_valid(candidate, is_trading_day):
                return candidate
        raise ValueError("no valid expiry found within one calendar week")

    def expiry_on_or_after(
        self,
        reference: date,
        *,
        is_trading_day: TradingDayPredicate,
    ) -> date:
        """Return the first adjusted expiry that is on or after ``reference``."""
        nominal = self.nominal_expiry(reference)
        expiry = self.adjust_expiry(nominal, is_trading_day=is_trading_day)
        if expiry >= reference:
            return expiry
        next_nominal = nominal + timedelta(days=7)
        return self.adjust_expiry(next_nominal, is_trading_day=is_trading_day)

    def _is_valid(self, value: date, is_trading_day: TradingDayPredicate) -> bool:
        return value not in self.holidays and is_trading_day(value)


def expiry_dates(
    start: date,
    end: date,
    rule: WeeklyExpiryRule,
    *,
    is_trading_day: TradingDayPredicate,
) -> tuple[date, ...]:
    """Generate adjusted weekly expiries in the inclusive ``[start, end]`` range."""
    if end < start:
        raise ValueError("end must be on or after start")

    result: list[date] = []
    nominal = rule.nominal_expiry(start)
    while nominal <= end + timedelta(days=7):
        expiry = rule.adjust_expiry(nominal, is_trading_day=is_trading_day)
        if start <= expiry <= end and (not result or result[-1] != expiry):
            result.append(expiry)
        nominal += timedelta(days=7)
    return tuple(result)
