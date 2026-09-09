from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class _Stump:
    feature_index: int
    threshold: Decimal
    left_value: Decimal
    right_value: Decimal


@dataclass(frozen=True, slots=True)
class GradientBoostingClassifier:
    """Deterministic one-vs-rest gradient boosting using regression stumps.

    Each binary learner minimizes squared error against the current residuals.
    The fitted stumps, learning rate, estimator count, and class order are all
    stored explicitly, making training reproducible without external ML
    dependencies or hidden data.
    """

    labels: tuple[Regime, ...]
    initial_scores: tuple[Decimal, ...]
    estimators: tuple[tuple[_Stump, ...], ...]
    learning_rate: Decimal

    @classmethod
    def fit(
        cls,
        dataset: FeatureDataset,
        n_estimators: int = 25,
        learning_rate: Decimal = Decimal("0.1"),
    ) -> "GradientBoostingClassifier":
        if n_estimators <= 0:
            raise ValueError("n_estimators must be positive")
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        width = len(dataset.features[0])
        all_estimators: list[tuple[_Stump, ...]] = []
        initial_scores: list[Decimal] = []
        for label in labels:
            targets = [Decimal("1") if current == label else Decimal("0") for current in dataset.labels]
            mean = sum(targets, Decimal("0")) / Decimal(len(targets))
            predictions = [mean] * len(targets)
            stumps: list[_Stump] = []
            for _ in range(n_estimators):
                residuals = [target - prediction for target, prediction in zip(targets, predictions)]
                stump = _best_stump(dataset.features, residuals, width)
                stumps.append(stump)
                for row_index, row in enumerate(dataset.features):
                    value = stump.left_value if row[stump.feature_index] <= stump.threshold else stump.right_value
                    predictions[row_index] += learning_rate * value
            initial_scores.append(mean)
            all_estimators.append(tuple(stumps))
        return cls(tuple(labels), tuple(initial_scores), tuple(all_estimators), learning_rate)

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.estimators:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        if not self.estimators[0]:
            raise ValueError("classifier is not fitted")
        scores = []
        for initial, stumps in zip(self.initial_scores, self.estimators):
            score = initial
            for stump in stumps:
                score += self.learning_rate * (
                    stump.left_value if vector[stump.feature_index] <= stump.threshold else stump.right_value
                )
            scores.append(score)
        return self.labels[scores.index(max(scores))]

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


def _best_stump(rows: Sequence[tuple[Decimal, ...]], residuals: Sequence[Decimal], width: int) -> _Stump:
    best: tuple[Decimal, _Stump] | None = None
    for feature_index in range(width):
        values = sorted(set(row[feature_index] for row in rows))
        for left_value, right_value in zip(values, values[1:]):
            threshold = (left_value + right_value) / Decimal("2")
            left_indices = [i for i, row in enumerate(rows) if row[feature_index] <= threshold]
            right_indices = [i for i, row in enumerate(rows) if row[feature_index] > threshold]
            if not left_indices or not right_indices:
                continue
            left_mean = sum((residuals[i] for i in left_indices), Decimal("0")) / Decimal(len(left_indices))
            right_mean = sum((residuals[i] for i in right_indices), Decimal("0")) / Decimal(len(right_indices))
            error = sum(
                ((residuals[i] - (left_mean if i in left_indices else right_mean)) ** 2 for i in range(len(rows))),
                Decimal("0"),
            )
            candidate = _Stump(feature_index, threshold, left_mean, right_mean)
            if best is None or error < best[0]:
                best = (error, candidate)
    if best is None:
        mean = sum(residuals, Decimal("0")) / Decimal(len(residuals))
        return _Stump(0, rows[0][0], mean, mean)
    return best[1]
