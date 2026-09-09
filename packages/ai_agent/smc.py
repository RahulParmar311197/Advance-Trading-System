from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from packages.market_data.models import Candle
from packages.smc.bos import detect_bos
from packages.smc.events import StructuredSMCEvent, all_smc_events
from packages.smc.fvg import detect_fvg
from packages.smc.liquidity import detect_liquidity_sweeps
from packages.smc.mss import detect_mss
from packages.smc.swings import detect_swings


@dataclass(frozen=True, slots=True)
class SMCRequest:
    """Explicit configuration for deterministic SMC detection over supplied candles."""

    swing_left: int = 2
    swing_right: int = 2

    def __post_init__(self) -> None:
        if self.swing_left <= 0:
            raise ValueError("swing_left must be positive")
        if self.swing_right <= 0:
            raise ValueError("swing_right must be positive")


@dataclass(frozen=True, slots=True)
class SMCResult:
    """Structured SMC detections aligned to the supplied candle window."""

    request: SMCRequest
    swings: tuple[tuple[int, str, object], ...]
    events: tuple[StructuredSMCEvent, ...]


def detect_smc(candles: Sequence[Candle], request: SMCRequest | None = None) -> SMCResult:
    """Run the existing deterministic SMC detectors without inventing market data."""
    resolved = request or SMCRequest()
    ordered = tuple(candles)
    _validate_candles(ordered)

    candle_list = list(ordered)
    swings = detect_swings(candle_list, resolved.swing_left, resolved.swing_right)
    bos = detect_bos(candle_list, swings)
    mss = detect_mss(candle_list, swings)
    liquidity = detect_liquidity_sweeps(candle_list, swings)
    fvg = detect_fvg(candle_list)
    events = all_smc_events(
        candle_list,
        bos=bos,
        mss=mss,
        liquidity=liquidity,
        fvg=fvg,
    )

    return SMCResult(
        request=resolved,
        swings=tuple((s.index, s.kind, s.price) for s in swings),
        events=tuple(events),
    )


def _validate_candles(candles: tuple[Candle, ...]) -> None:
    if not candles:
        raise ValueError("candles must not be empty")
    for previous, current in zip(candles, candles[1:]):
        if current.timestamp <= previous.timestamp:
            raise ValueError("candles must be strictly increasing by timestamp")
        if current.symbol != previous.symbol or current.timeframe != previous.timeframe:
            raise ValueError("candles must share symbol and timeframe")
    for candle in candles:
        if candle.high < candle.low:
            raise ValueError("candle high must be >= low")
        if candle.open < candle.low or candle.open > candle.high:
            raise ValueError("candle open must be within high/low")
        if candle.close < candle.low or candle.close > candle.high:
            raise ValueError("candle close must be within high/low")
        if candle.volume < 0:
            raise ValueError("candle volume must be non-negative")
