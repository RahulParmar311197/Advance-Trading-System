from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class NearestCentroidClassifier:
    """Dependency-free deterministic multiclass nearest-centroid baseline."""

    labels: tuple[Regime, ...] = ()
    centroids: tuple[tuple[Decimal, ...], ...] = ()

    @classmethod
    def fit(cls, dataset: FeatureDataset) -> "NearestCentroidClassifier":
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        centroids: list[tuple[Decimal, ...]] = []
        for label in labels:
            rows = [row for row, current in zip(dataset.features, dataset.labels) if current == label]
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
            sum(((value - center) ** 2 for value, center in zip(vector, centroid)), Decimal("0"))
            for centroid in self.centroids
        )
        return self.labels[distances.index(min(distances))]

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


@dataclass(frozen=True, slots=True)
class LogisticRegressionClassifier:
    """Dependency-free deterministic one-vs-rest logistic-regression baseline."""

    labels: tuple[Regime, ...] = ()
    weights: tuple[tuple[Decimal, ...], ...] = ()
    biases: tuple[Decimal, ...] = ()
    learning_rate: Decimal = Decimal("0.1")
    epochs: int = 500
    l2: Decimal = Decimal("0")

    @classmethod
    def fit(
        cls,
        dataset: FeatureDataset,
        learning_rate: Decimal = Decimal("0.1"),
        epochs: int = 500,
        l2: Decimal = Decimal("0"),
    ) -> "LogisticRegressionClassifier":
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if epochs <= 0:
            raise ValueError("epochs must be positive")
        if l2 < 0:
            raise ValueError("l2 must be non-negative")
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        rows = dataset.features
        width = len(rows[0])
        trained_weights: list[tuple[Decimal, ...]] = []
        trained_biases: list[Decimal] = []
        n = Decimal(len(rows))
        for label in labels:
            weights = [Decimal("0") for _ in range(width)]
            bias = Decimal("0")
            for _ in range(epochs):
                gradients = [Decimal("0") for _ in range(width)]
                bias_gradient = Decimal("0")
                for row, current in zip(rows, dataset.labels):
                    target = Decimal("1") if current == label else Decimal("0")
                    probability = _sigmoid(_dot(row, weights) + bias)
                    error = probability - target
                    bias_gradient += error
                    for index, value in enumerate(row):
                        gradients[index] += error * value
                for index in range(width):
                    gradients[index] = gradients[index] / n + l2 * weights[index]
                    weights[index] -= learning_rate * gradients[index]
                bias -= learning_rate * bias_gradient / n
            trained_weights.append(tuple(weights))
            trained_biases.append(bias)
        return cls(
            labels=labels,
            weights=tuple(trained_weights),
            biases=tuple(trained_biases),
            learning_rate=learning_rate,
            epochs=epochs,
            l2=l2,
        )

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.weights:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        if len(vector) != len(self.weights[0]):
            raise ValueError("feature width does not match fitted classifier")
        scores = tuple(_dot(vector, weight) + bias for weight, bias in zip(self.weights, self.biases))
        return self.labels[scores.index(max(scores))]

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


def _dot(left: Sequence[Decimal], right: Sequence[Decimal]) -> Decimal:
    return sum((a * b for a, b in zip(left, right)), Decimal("0"))


def _sigmoid(value: Decimal) -> Decimal:
    if value >= Decimal("60"):
        return Decimal("1")
    if value <= Decimal("-60"):
        return Decimal("0")
    return Decimal("1") / (Decimal("1") + (-value).exp())
