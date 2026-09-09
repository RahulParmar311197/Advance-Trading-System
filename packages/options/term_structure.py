from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ImpliedVolatilityObservation:
    """Observed implied volatility for one option expiry."""

    expiry: datetime
    implied_volatility: float

    def __post_init__(self) -> None:
        if self.implied_volatility <= 0:
            raise ValueError("implied_volatility must be positive")


def term_structure(
    observations: tuple[ImpliedVolatilityObservation, ...],
) -> tuple[ImpliedVolatilityObservation, ...]:
    """Return supplied implied-volatility observations ordered by expiry.

    No interpolation, smoothing, or market-data inference is performed. An
    expiry may occur only once; duplicate observations fail closed because
    silently choosing one would discard supplied data.
    """
    if not observations:
        raise ValueError("observations must not be empty")
    ordered = tuple(sorted(observations, key=lambda item: item.expiry))
    for previous, current in zip(ordered, ordered[1:]):
        if previous.expiry == current.expiry:
            raise ValueError("duplicate expiry observation")
    return ordered
