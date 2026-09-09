from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from packages.regime.detector import Regime, RegimeThresholds, detect_regime
from packages.regime.features import RegimeFeatureVector

TrendDirection = Literal["up", "down", "neutral"]
VolatilityState = Literal["high", "low", "normal"]


@dataclass(frozen=True, slots=True)
class RegimeClassification:
    """Structured regime labels derived from one deterministic feature vector."""

    regime: Regime
    trend_direction: TrendDirection
    volatility_state: VolatilityState


def classify_regime(
    features: RegimeFeatureVector, thresholds: RegimeThresholds
) -> RegimeClassification:
    """Return the primary regime plus independent trend and volatility labels.

    The primary regime is produced by the existing transparent detector. The
    secondary labels use the same explicit caller-supplied thresholds, so the
    classifier introduces no hidden market assumptions or inferred data.
    """
    regime = detect_regime(features, thresholds)
    trend_direction = _trend_direction(features, thresholds)
    volatility_state = _volatility_state(features, thresholds)
    return RegimeClassification(
        regime=regime,
        trend_direction=trend_direction,
        volatility_state=volatility_state,
    )


def _trend_direction(
    features: RegimeFeatureVector, thresholds: RegimeThresholds
) -> TrendDirection:
    if abs(features.period_return) < thresholds.trending_return:
        return "neutral"
    if features.period_return > 0:
        return "up"
    if features.period_return < 0:
        return "down"
    return "neutral"


def _volatility_state(
    features: RegimeFeatureVector, thresholds: RegimeThresholds
) -> VolatilityState:
    if features.mean_absolute_return >= thresholds.high_volatility_mean_abs_return:
        return "high"
    if features.mean_absolute_return <= thresholds.low_volatility_mean_abs_return:
        return "low"
    return "normal"
