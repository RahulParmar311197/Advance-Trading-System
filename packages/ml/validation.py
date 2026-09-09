from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.ml.training import TrainingConfig, train_classifier, predict_labels
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class OutOfSampleResult:
    """Predictions and accuracy from a strictly held-out feature block."""

    train_size: int
    test_size: int
    predictions: tuple[Regime, ...]
    actual: tuple[Regime, ...]
    accuracy: Decimal


def evaluate_out_of_sample(
    dataset: FeatureDataset,
    test_size: int,
    config: TrainingConfig,
) -> OutOfSampleResult:
    """Fit only on the leading block and evaluate only on the final holdout."""
    if test_size <= 0:
        raise ValueError("test_size must be positive")
    if test_size >= len(dataset.labels):
        raise ValueError("test_size must leave at least one training row")
    train_size = len(dataset.labels) - test_size
    train = FeatureDataset(
        features=dataset.features[:train_size],
        labels=dataset.labels[:train_size],
    )
    test_features = dataset.features[train_size:]
    actual = dataset.labels[train_size:]
    model = train_classifier(train, config)
    predictions = predict_labels(model, test_features)
    correct = sum(prediction == label for prediction, label in zip(predictions, actual))
    return OutOfSampleResult(
        train_size=train_size,
        test_size=test_size,
        predictions=predictions,
        actual=actual,
        accuracy=Decimal(correct) / Decimal(test_size),
    )
