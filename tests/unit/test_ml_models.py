from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.models import NearestCentroidClassifier


def dataset() -> FeatureDataset:
    return FeatureDataset(
        features=(
            (Decimal("1"), Decimal("0")),
            (Decimal("2"), Decimal("0")),
            (Decimal("9"), Decimal("0")),
            (Decimal("10"), Decimal("0")),
        ),
        labels=("bull", "bull", "bear", "bear"),
    )


def test_nearest_centroid_classifier_is_deterministic():
    model = NearestCentroidClassifier().fit(dataset())
    assert model.predict((Decimal("1.5"), Decimal("0"))) == "bull"
    assert model.predict((Decimal("9.5"), Decimal("0"))) == "bear"
    assert model.predict_many(((Decimal("1.5"), Decimal("0")),)) == ("bull",)


def test_fit_requires_at_least_two_classes():
    data = FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),)), labels=("bull", "bull")
    )
    with pytest.raises(ValueError, match="two classes"):
        NearestCentroidClassifier().fit(data)


def test_predict_rejects_wrong_feature_width():
    model = NearestCentroidClassifier().fit(dataset())
    with pytest.raises(ValueError, match="feature width"):
        model.predict((Decimal("1"),))


def test_predict_before_fit_fails_closed():
    with pytest.raises(ValueError, match="fitted"):
        NearestCentroidClassifier().predict((Decimal("1"), Decimal("0")))
