from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from packages.regime.features import RegimeFeatureVector

Regime = Literal["bull", "bear", "high_volatility", "low_volatility", "range"]


@dataclass(frozen=True, slots=True)
class RegimeThresholds:
    """Explicit thresholds for the feature-based regime detector.

    Thresholds are supplied by the caller so regime labels are reproducible
    and are not hidden assumptions about a particular Indian market series.
    """

    low_volatility_mean_abs_return: Decimal
    high_volatility_mean_abs_return: Decimal
    trending_return: Decimal
    trending_efficiency: Decimal

    def __post_init__(self) -> None:
        values = (
            self.low_volatility_mean_abs_return,
            self.high_volatility_mean_abs_return,
            self.trending_return,
            self.trending_efficiency,
        )
        if any(value < 0 for value in values):
            raise ValueError("regime thresholds must be non-negative")
        if self.low_volatility_mean_abs_return > self.high_volatility_mean_abs_return:
            raise ValueError("low volatility threshold must not exceed high volatility threshold")
        if self.trending_efficiency > 1:
            raise ValueError("trending_efficiency must not exceed one")


def detect_regime(
    features: RegimeFeatureVector, thresholds: RegimeThresholds
) -> Regime:
    """Classify supplied deterministic features into a transparent regime.

    The detector uses only the feature vector and caller-supplied thresholds.
    High/low volatility take precedence over directional trend classification;
    a remaining observation is classified as a range. Bull/bear labels require
    both sufficient absolute return and path efficiency.
    """
    mean_abs_return = features.mean_absolute_return
    if mean_abs_return >= thresholds.high_volatility_mean_abs_return:
        return "high_volatility"
    if mean_abs_return <= thresholds.low_volatility_mean_abs_return:
        return "low_volatility"

    is_trending = (
        abs(features.period_return) >= thresholds.trending_return
        and features.range_efficiency >= thresholds.trending_efficiency
    )
    if is_trending:
        return "bull" if features.period_return > 0 else "bear"
    return "range"
