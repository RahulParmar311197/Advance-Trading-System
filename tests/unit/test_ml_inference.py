from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.inference import InferenceResult, run_inference
from packages.ml.models import LogisticRegressionClassifier


def model() -> LogisticRegressionClassifier:
    dataset = FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("10"),)),
        labels=("bull", "bull", "bear", "bear"),
    )
    return LogisticRegressionClassifier.fit(dataset, learning_rate=Decimal("0.2"), epochs=200)


def test_inference_uses_fitted_model_and_returns_immutable_result():
    result = run_inference(model(), ((Decimal("1.5"),), (Decimal("9.5"),)))
    assert result == InferenceResult(predictions=("bull", "bear"))
    assert isinstance(result.predictions, tuple)


def test_inference_rejects_empty_features():
    with pytest.raises(ValueError, match="features"):
        run_inference(model(), ())


def test_inference_rejects_empty_or_ragged_rows_before_model_call():
    with pytest.raises(ValueError, match="feature rows"):
        run_inference(model(), ((),))
    with pytest.raises(ValueError, match="equal width"):
        run_inference(model(), ((Decimal("1"),), (Decimal("2"), Decimal("3"))))


def test_inference_preserves_model_feature_width_validation():
    with pytest.raises(ValueError, match="feature width"):
        run_inference(model(), ((Decimal("1"), Decimal("2")),))
