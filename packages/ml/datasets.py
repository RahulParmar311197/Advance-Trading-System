from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.regime.classifier import Regime
from packages.regime.features import RegimeFeatureVector


@dataclass(frozen=True, slots=True)
class FeatureDataset:
    """Immutable supervised-learning matrix with explicit regime labels."""

    features: tuple[tuple[Decimal, ...], ...]
    labels: tuple[Regime, ...]

    def __post_init__(self) -> None:
        if len(self.features) != len(self.labels):
            raise ValueError("features and labels must have equal length")
        if not self.features:
            raise ValueError("features must not be empty")
        width = len(self.features[0])
        if width == 0:
            raise ValueError("feature rows must not be empty")
        if any(len(row) != width for row in self.features):
            raise ValueError("feature rows must have equal width")


def build_regime_feature_dataset(
    rows: Sequence[tuple[RegimeFeatureVector, Regime]],
) -> FeatureDataset:
    """Build an explicit supervised dataset from caller-supplied labels.

    Labels are never inferred here. The feature order is fixed and documented
    by the tuple construction so model training remains reproducible.
    """
    if not rows:
        raise ValueError("rows must not be empty")
    features = tuple(
        (
            row[0].period_return,
            row[0].mean_absolute_return,
            row[0].trend_slope,
            row[0].range_efficiency,
            row[0].average_volume,
        )
        for row in rows
    )
    labels = tuple(row[1] for row in rows)
    return FeatureDataset(features=features, labels=labels)
