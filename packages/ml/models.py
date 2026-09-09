from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.regime.detector import Regime
from packages.ml.datasets import FeatureDataset


@dataclass(frozen=True, slots=True)
class NearestCentroidClassifier:
    """Deterministic multiclass baseline using class feature centroids.

    This is intentionally dependency-free and interpretable. It is a baseline,
    not a claim of predictive performance. Training data and labels are supplied
    explicitly by the caller.
    """

    labels: tuple[Regime, ...]
    centroids: tuple[tuple[Decimal, ...], ...]

    @classmethod
    def fit(cls, dataset: FeatureDataset) -> "NearestCentroidClassifier":
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        centroids: list[tuple[Decimal, ...]] = []
        for label in labels:
            rows = [row for row, current in zip(dataset.features, dataset.labels) if current == label]
            width = len(rows[0])
            centroid = tuple(
                sum((row[index] for row in rows), Decimal("0")) / Decimal(len(rows))
                for index in range(width)
            )
            centroids.append(centroid)
        return cls(labels=labels, centroids=tuple(centroids))

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if len(features) != len(self.centroids[0]):
            raise ValueError("feature width does not match fitted classifier")
        distances = tuple(
            sum(((value - center) ** 2 for value, center in zip(features, centroid)), Decimal("0"))
            for centroid in self.centroids
        )
        return self.labels[distances.index(min(distances))]
