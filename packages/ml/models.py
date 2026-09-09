from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class NearestCentroidClassifier:
    """Dependency-free deterministic multiclass nearest-centroid baseline."""

    labels: tuple[Regime, ...]
    centroids: tuple[tuple[Decimal, ...], ...]

    @classmethod
    def fit(cls, dataset: FeatureDataset) -> "NearestCentroidClassifier":
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        centroids: list[tuple[Decimal, ...]] = []
        for label in labels:
            rows = [
                row for row, current in zip(dataset.features, dataset.labels)
                if current == label
            ]
            centroid = tuple(
                sum((row[index] for row in rows), Decimal("0")) / Decimal(len(rows))
                for index in range(len(rows[0]))
            )
            centroids.append(centroid)
        return cls(labels=labels, centroids=tuple(centroids))

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.centroids:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        if len(vector) != len(self.centroids[0]):
            raise ValueError("feature width does not match fitted classifier")
        distances = tuple(
            sum(
                ((value - center) ** 2 for value, center in zip(vector, centroid)),
                Decimal("0"),
            )
            for centroid in self.centroids
        )
        return self.labels[distances.index(min(distances))]

    def predict_many(
        self, features: Sequence[Sequence[Decimal]]
    ) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)
