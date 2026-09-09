from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.market_data.models import Candle
from packages.regime.classifier import RegimeClassification, classify_regime
from packages.regime.detector import RegimeThresholds
from packages.regime.features import RegimeFeatureVector, calculate_regime_features


@dataclass(frozen=True, slots=True)
class RegimeDatasetRow:
    """One deterministic feature/label row derived from a candle window."""

    observation_index: int
    features: RegimeFeatureVector
    classification: RegimeClassification


def build_regime_dataset(
    windows: Sequence[Sequence[Candle]], thresholds: RegimeThresholds
) -> tuple[RegimeDatasetRow, ...]:
    """Build reproducible regime rows from caller-supplied candle windows.

    Windows are independent observations. No labels or missing observations are
    inferred; every row is calculated directly from its supplied window.
    """
    if not windows:
        raise ValueError("windows must not be empty")
    rows: list[RegimeDatasetRow] = []
    for index, candles in enumerate(windows):
        features = calculate_regime_features(candles)
        classification = classify_regime(features, thresholds)
        rows.append(
            RegimeDatasetRow(
                observation_index=index,
                features=features,
                classification=classification,
            )
        )
    return tuple(rows)
