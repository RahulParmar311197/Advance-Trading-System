from __future__ import annotations

from datetime import datetime, timedelta

from packages.instruments.trading_calendar import IST, MARKET_CLOSE, MARKET_OPEN, is_market_session

from .models import Candle


def validate_ohlcv(candles: list[Candle]) -> None:
    previous = None
    for c in candles:
        if c.timestamp.tzinfo is None or c.timestamp.utcoffset() is None:
            raise ValueError(f"timestamp must be timezone-aware at {c.timestamp}")
        if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.low > c.high:
            raise ValueError(f"invalid OHLC range at {c.timestamp}")
        if c.volume < 0:
            raise ValueError(f"negative volume at {c.timestamp}")
        if previous is not None and c.timestamp <= previous:
            raise ValueError("timestamps must be strictly increasing")
        previous = c.timestamp


def _timeframe_delta(timeframe: str) -> timedelta:
    value = timeframe.strip().lower()
    if len(value) < 2:
        raise ValueError("unsupported timeframe")
    unit = value[-1]
    try:
        amount = int(value[:-1])
    except ValueError as exc:
        raise ValueError("unsupported timeframe") from exc
    if amount <= 0 or unit not in {"m", "h"}:
        raise ValueError("unsupported timeframe")
    return timedelta(minutes=amount if unit == "m" else amount * 60)


def _next_session_start(timestamp: datetime) -> datetime:
    local = timestamp.astimezone(IST)
    day = local.date() + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day, MARKET_OPEN, tzinfo=IST).astimezone(timestamp.tzinfo)


def _next_expected(timestamp: datetime, delta: timedelta) -> datetime:
    candidate = timestamp + delta
    local = candidate.astimezone(IST)
    if local.time() > MARKET_CLOSE:
        return _next_session_start(timestamp)
    if not is_market_session(candidate):
        if local.time() < MARKET_OPEN:
            return datetime.combine(local.date(), MARKET_OPEN, tzinfo=IST).astimezone(timestamp.tzinfo)
        return _next_session_start(timestamp)
    return candidate


def find_missing_candles(candles: list[Candle], timeframe: str) -> tuple[datetime, ...]:
    """Return expected session timestamps absent between supplied candles.

    The check is session-aware: overnight, weekend, and out-of-session gaps are
    not reported as missing candles. It assumes the exchange session defined by
    ``packages.instruments.trading_calendar`` and does not infer holidays.
    """
    if not candles:
        return ()
    validate_ohlcv(candles)
    delta = _timeframe_delta(timeframe)
    missing: list[datetime] = []
    for previous, current in zip(candles, candles[1:]):
        expected = _next_expected(previous.timestamp, delta)
        while expected < current.timestamp:
            if is_market_session(expected):
                missing.append(expected)
            expected = _next_expected(expected, delta)
    return tuple(missing)
