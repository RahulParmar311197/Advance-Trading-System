from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.training import TrainingConfig
from packages.ml.validation import evaluate_out_of_sample


def dataset() -> FeatureDataset:
    return FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("10"),)),
        labels=("bull", "bear", "bear", "bear"),
    )


def test_out_of_sample_uses_final_block_only_for_evaluation():
    result = evaluate_out_of_sample(
        dataset(),
        test_size=2,
        config=TrainingConfig(model="logistic", learning_rate=Decimal("0.2"), epochs=200),
    )
    assert result.train_size == 2
    assert result.test_size == 2
    assert result.actual == ("bear", "bear")
    assert result.predictions == ("bear", "bear")
    assert result.accuracy == Decimal("1")


def test_out_of_sample_rejects_invalid_holdout_size():
    config = TrainingConfig(model="logistic", epochs=10)
    with pytest.raises(ValueError, match="positive"):
        evaluate_out_of_sample(dataset(), 0, config)
    with pytest.raises(ValueError, match="training row"):
        evaluate_out_of_sample(dataset(), len(dataset().labels), config)
