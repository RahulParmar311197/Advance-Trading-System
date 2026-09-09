from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Mapping, Sequence

from packages.indicators.atr import atr
from packages.indicators.ema import ema
from packages.indicators.vwap import vwap
from packages.market_data.models import Candle


@dataclass(frozen=True, slots=True)
class FeatureRequest:
    """Explicit deterministic feature selection for an ordered candle window."""

    names: tuple[str, ...]
    ema_period: int = 20
    atr_period: int = 14

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("names must not be empty")
        normalized = tuple(name.strip().lower() for name in self.names)
        if any(not name for name in normalized):
            raise ValueError("feature names must not be empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("feature names must be unique")
        supported = {"ema", "atr", "vwap"}
        unknown = sorted(set(normalized) - supported)
        if unknown:
            raise ValueError(f"unsupported features: {', '.join(unknown)}")
        if self.ema_period <= 0:
            raise ValueError("ema_period must be positive")
        if self.atr_period <= 0:
            raise ValueError("atr_period must be positive")
        object.__setattr__(self, "names", normalized)


@dataclass(frozen=True, slots=True)
class FeatureRow:
    """One candle-aligned feature observation."""

    timestamp: datetime
    values: tuple[tuple[str, Decimal | None], ...]

    def as_mapping(self) -> Mapping[str, Decimal | None]:
        return dict(self.values)


@dataclass(frozen=True, slots=True)
class FeatureResult:
    """Deterministic feature observations aligned to the supplied candles."""

    request: FeatureRequest
    rows: tuple[FeatureRow, ...]


def calculate_features(
    candles: Sequence[Candle], request: FeatureRequest
) -> FeatureResult:
    """Calculate selected deterministic indicators without inferring market data."""
    ordered = tuple(candles)
    _validate_candles(ordered)

    closes = [candle.close for candle in ordered]
    computed: dict[str, list[Decimal | None]] = {}
    if "ema" in request.names:
        computed["ema"] = ema(closes, request.ema_period)
    if "atr" in request.names:
        computed["atr"] = atr(list(ordered), request.atr_period)
    if "vwap" in request.names:
        computed["vwap"] = vwap(list(ordered))

    rows = tuple(
        FeatureRow(
            timestamp=candle.timestamp,
            values=tuple((name, computed[name][index]) for name in request.names),
        )
        for index, candle in enumerate(ordered)
    )
    return FeatureResult(request=request, rows=rows)


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
