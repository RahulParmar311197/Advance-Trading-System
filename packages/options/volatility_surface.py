from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class VolatilitySurfacePoint:
    """Observed implied volatility at one expiry/strike coordinate."""

    expiry: datetime
    strike: float
    implied_volatility: float

    def __post_init__(self) -> None:
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.implied_volatility <= 0:
            raise ValueError("implied_volatility must be positive")


def volatility_surface(
    observations: tuple[VolatilitySurfacePoint, ...],
) -> tuple[VolatilitySurfacePoint, ...]:
    """Return supplied volatility-surface observations in deterministic order.

    The function deliberately performs no interpolation, smoothing, or
    extrapolation. Every returned point is an observation supplied by the
    caller. Duplicate expiry/strike coordinates fail closed because silently
    choosing one would discard market observations.
    """
    if not observations:
        raise ValueError("observations must not be empty")

    ordered = tuple(sorted(observations, key=lambda item: (item.expiry, item.strike)))
    for previous, current in zip(ordered, ordered[1:]):
        if previous.expiry == current.expiry and previous.strike == current.strike:
            raise ValueError("duplicate expiry/strike observation")
    return ordered
