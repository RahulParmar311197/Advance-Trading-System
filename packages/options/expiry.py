from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class OptionExpiryCalendar:
    """Validated, immutable expiry dates supplied by an authorized data source.

    The calendar deliberately stores dates rather than inferring an exchange
    schedule. Production Indian expiry schedules must come from the configured
    provider or an explicitly supplied calendar, so this class cannot invent
    weekly/monthly expiry rules.
    """

    expiries: tuple[datetime, ...]

    def __post_init__(self) -> None:
        if not self.expiries:
            raise ValueError("expiries must not be empty")
        if any(value.tzinfo is None or value.utcoffset() is None for value in self.expiries):
            raise ValueError("all expiries must be timezone-aware")
        if tuple(sorted(self.expiries)) != self.expiries:
            raise ValueError("expiries must be sorted ascending")
        if len(set(self.expiries)) != len(self.expiries):
            raise ValueError("expiries must not contain duplicates")

    @classmethod
    def from_expiries(cls, expiries: list[datetime] | tuple[datetime, ...]) -> "OptionExpiryCalendar":
        """Build a calendar from explicitly supplied provider expiry timestamps."""
        return cls(tuple(expiries))

    def next_on_or_after(self, timestamp: datetime) -> datetime:
        """Return the first configured expiry at or after ``timestamp``."""
        self._validate_query_timestamp(timestamp)
        for expiry in self.expiries:
            if expiry >= timestamp:
                return expiry
        raise LookupError("no configured option expiry on or after timestamp")

    def between(self, start: datetime, end: datetime) -> tuple[datetime, ...]:
        """Return configured expiries in the half-open ``[start, end)`` window."""
        self._validate_query_timestamp(start)
        self._validate_query_timestamp(end)
        if end <= start:
            raise ValueError("end must be after start")
        return tuple(expiry for expiry in self.expiries if start <= expiry < end)

    @staticmethod
    def _validate_query_timestamp(timestamp: datetime) -> None:
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
