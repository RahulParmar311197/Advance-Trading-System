from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable

from packages.market_data.models import Candle


@dataclass(frozen=True, slots=True)
class StructuredSMCEvent:
    """Stable, serializable representation of a deterministic SMC event."""

    event: str
    symbol: str
    timeframe: str
    timestamp: datetime
    price: Decimal
    index: int
    direction: str | None = None
    confidence: Decimal | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "price": self.price,
            "index": self.index,
            "direction": self.direction,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


def _event_from_detection(
    name: str,
    detection: Any,
    candles: list[Candle],
    *,
    price: Decimal,
    direction: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> StructuredSMCEvent:
    index = int(detection.index)
    if index < 0 or index >= len(candles):
        raise ValueError(f"event index out of range: {index}")
    candle = candles[index]
    return StructuredSMCEvent(
        event=name,
        symbol=candle.symbol,
        timeframe=candle.timeframe,
        timestamp=candle.timestamp,
        price=Decimal(price),
        index=index,
        direction=direction,
        metadata=metadata or {},
    )


def structure_events(candles: list[Candle], detections: Iterable[Any], event_name: str) -> list[StructuredSMCEvent]:
    """Convert deterministic detector outputs into the common event contract."""
    return [
        _event_from_detection(
            event_name,
            detection,
            candles,
            price=Decimal(detection.level),
            direction=getattr(detection, "direction", None),
        )
        for detection in detections
    ]


def liquidity_events(candles: list[Candle], detections: Iterable[Any]) -> list[StructuredSMCEvent]:
    return [
        _event_from_detection(
            "liquidity_sweep",
            detection,
            candles,
            price=Decimal(detection.level),
            direction=detection.direction,
        )
        for detection in detections
    ]


def fvg_events(candles: list[Candle], detections: Iterable[Any]) -> list[StructuredSMCEvent]:
    return [
        _event_from_detection(
            "fvg",
            detection,
            candles,
            price=(Decimal(detection.low) + Decimal(detection.high)) / Decimal(2),
            direction=detection.direction,
            metadata={"low": Decimal(detection.low), "high": Decimal(detection.high)},
        )
        for detection in detections
    ]


def all_smc_events(
    candles: list[Candle],
    *,
    bos: Iterable[Any] = (),
    mss: Iterable[Any] = (),
    liquidity: Iterable[Any] = (),
    fvg: Iterable[Any] = (),
) -> list[StructuredSMCEvent]:
    events = (
        structure_events(candles, bos, "bos")
        + structure_events(candles, mss, "mss")
        + liquidity_events(candles, liquidity)
        + fvg_events(candles, fvg)
    )
    return sorted(events, key=lambda item: (item.timestamp, item.event, item.index))
