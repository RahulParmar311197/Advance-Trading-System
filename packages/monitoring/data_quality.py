from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from packages.market_data.models import Candle
from packages.market_data.validation import find_missing_candles, validate_ohlcv


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    symbol: str
    timeframe: str
    checked_at: datetime
    candle_count: int
    valid: bool
    missing_candles: tuple[datetime, ...]
    error: str | None = None

    @property
    def healthy(self) -> bool:
        return self.valid and not self.missing_candles

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "ok" if self.healthy else "degraded",
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "checked_at": self.checked_at.isoformat(),
            "candle_count": self.candle_count,
            "missing_candles": [timestamp.isoformat() for timestamp in self.missing_candles],
            "error": self.error,
        }


def assess_candles(
    candles: Sequence[Candle],
    timeframe: str,
    checked_at: datetime,
) -> DataQualityReport:
    """Validate a persisted candle window and report missing session candles."""
    if not candles:
        raise ValueError("cannot assess an empty candle window")
    if checked_at.tzinfo is None or checked_at.utcoffset() is None:
        raise ValueError("checked_at must be timezone-aware")

    first = candles[0]
    if any(c.symbol != first.symbol or c.timeframe != first.timeframe for c in candles):
        raise ValueError("candle window must contain one symbol and timeframe")

    try:
        validate_ohlcv(list(candles))
        missing = find_missing_candles(list(candles), timeframe)
    except ValueError as exc:
        return DataQualityReport(
            symbol=first.symbol,
            timeframe=first.timeframe,
            checked_at=checked_at,
            candle_count=len(candles),
            valid=False,
            missing_candles=(),
            error=str(exc),
        )

    return DataQualityReport(
        symbol=first.symbol,
        timeframe=first.timeframe,
        checked_at=checked_at,
        candle_count=len(candles),
        valid=True,
        missing_candles=missing,
    )
