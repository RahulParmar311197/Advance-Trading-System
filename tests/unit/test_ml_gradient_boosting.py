from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.gradient_boosting import GradientBoostingClassifier


def dataset() -> FeatureDataset:
    return FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("10"),)),
        labels=("bull", "bull", "bear", "bear"),
    )


def test_gradient_boosting_learns_separable_fixture():
    model = GradientBoostingClassifier.fit(dataset(), n_estimators=10, learning_rate=Decimal("0.2"))
    assert model.predict((Decimal("1.5"),)) == "bull"
    assert model.predict((Decimal("9.5"),)) == "bear"


def test_gradient_boosting_is_deterministic():
    config = {"n_estimators": 8, "learning_rate": Decimal("0.15")}
    assert GradientBoostingClassifier.fit(dataset(), **config) == GradientBoostingClassifier.fit(dataset(), **config)


def test_gradient_boosting_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="n_estimators"):
        GradientBoostingClassifier.fit(dataset(), n_estimators=0)
    with pytest.raises(ValueError, match="learning_rate"):
        GradientBoostingClassifier.fit(dataset(), learning_rate=Decimal("0"))
    with pytest.raises(ValueError, match="two distinct labels"):
        GradientBoostingClassifier.fit(FeatureDataset(features=((Decimal("1"),),), labels=("bull",)))


def test_gradient_boosting_rejects_wrong_width():
    model = GradientBoostingClassifier.fit(dataset(), n_estimators=3)
    with pytest.raises(IndexError):
        model.predict(())
