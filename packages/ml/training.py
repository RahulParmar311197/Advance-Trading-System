from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.ml.gradient_boosting import GradientBoostingClassifier
from packages.ml.models import LogisticRegressionClassifier, NearestCentroidClassifier, RandomForestClassifier
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    """Explicit reproducible configuration for a supported baseline model."""

    model: str
    learning_rate: Decimal = Decimal("0.1")
    epochs: int = 500
    l2: Decimal = Decimal("0")
    n_trees: int = 25
    max_depth: int = 4
    min_samples_split: int = 2
    max_features: int | None = None
    n_estimators: int = 25
    seed: int = 0

    def __post_init__(self) -> None:
        if self.model not in {"nearest_centroid", "logistic", "random_forest", "gradient_boosting"}:
            raise ValueError("unsupported model")


def train_classifier(dataset: FeatureDataset, config: TrainingConfig):
    """Fit a selected baseline using only the supplied labeled dataset."""
    if config.model == "nearest_centroid":
        return NearestCentroidClassifier.fit(dataset)
    if config.model == "logistic":
        return LogisticRegressionClassifier.fit(dataset, learning_rate=config.learning_rate, epochs=config.epochs, l2=config.l2)
    if config.model == "random_forest":
        return RandomForestClassifier.fit(dataset, n_trees=config.n_trees, max_depth=config.max_depth, min_samples_split=config.min_samples_split, max_features=config.max_features, seed=config.seed)
    return GradientBoostingClassifier.fit(dataset, n_estimators=config.n_estimators, learning_rate=config.learning_rate)


def predict_labels(model: object, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
    """Predict labels through a fitted baseline's public batch interface."""
    predict_many = getattr(model, "predict_many", None)
    if predict_many is None:
        raise TypeError("model must expose predict_many")
    return predict_many(features)
