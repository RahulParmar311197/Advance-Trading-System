from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.training import TrainingConfig, predict_labels, train_classifier


def dataset() -> FeatureDataset:
    return FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("10"),)),
        labels=("bull", "bull", "bear", "bear"),
    )


def test_training_config_rejects_unknown_model():
    with pytest.raises(ValueError, match="unsupported model"):
        TrainingConfig(model="svm")


def test_training_dispatches_logistic_baseline():
    model = train_classifier(
        dataset(), TrainingConfig(model="logistic", learning_rate=Decimal("0.2"), epochs=200)
    )
    assert predict_labels(model, ((Decimal("1.5"),), (Decimal("9.5"),))) == ("bull", "bear")


def test_training_dispatches_random_forest_with_explicit_seed():
    config = TrainingConfig(model="random_forest", n_trees=10, max_depth=3, max_features=1, seed=11)
    first = train_classifier(dataset(), config)
    second = train_classifier(dataset(), config)
    assert first == second


def test_predict_labels_requires_batch_prediction_interface():
    with pytest.raises(TypeError, match="predict_many"):
        predict_labels(object(), ((Decimal("1"),),))
