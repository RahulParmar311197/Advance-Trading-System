from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.models import LogisticRegressionClassifier, NearestCentroidClassifier, RandomForestClassifier


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
    data = FeatureDataset(features=((Decimal("1"),), (Decimal("2"),)), labels=("bull", "bull"))
    with pytest.raises(ValueError, match="two distinct labels"):
        NearestCentroidClassifier().fit(data)


def test_predict_rejects_wrong_feature_width():
    model = NearestCentroidClassifier().fit(dataset())
    with pytest.raises(ValueError, match="feature width"):
        model.predict((Decimal("1"),))


def test_predict_before_fit_fails_closed():
    with pytest.raises(ValueError, match="fitted"):
        NearestCentroidClassifier(labels=(), centroids=()).predict((Decimal("1"), Decimal("0")))


def test_logistic_regression_learns_separable_binary_fixture_deterministically():
    model = LogisticRegressionClassifier.fit(dataset(), learning_rate=Decimal("0.2"), epochs=300)
    assert model.predict((Decimal("1.5"), Decimal("0"))) == "bull"
    assert model.predict((Decimal("9.5"), Decimal("0"))) == "bear"
    assert model.predict_many(((Decimal("1.5"), Decimal("0")),)) == ("bull",)


def test_logistic_regression_rejects_invalid_training_configuration():
    with pytest.raises(ValueError, match="learning_rate"):
        LogisticRegressionClassifier.fit(dataset(), learning_rate=Decimal("0"))
    with pytest.raises(ValueError, match="epochs"):
        LogisticRegressionClassifier.fit(dataset(), epochs=0)
    with pytest.raises(ValueError, match="l2"):
        LogisticRegressionClassifier.fit(dataset(), l2=Decimal("-1"))


def test_logistic_regression_requires_two_classes():
    data = FeatureDataset(features=((Decimal("1"),), (Decimal("2"),)), labels=("bull", "bull"))
    with pytest.raises(ValueError, match="two distinct labels"):
        LogisticRegressionClassifier.fit(data)


def test_logistic_regression_predict_rejects_wrong_width():
    model = LogisticRegressionClassifier.fit(dataset(), epochs=10)
    with pytest.raises(ValueError, match="feature width"):
        model.predict((Decimal("1"),))


def test_random_forest_learns_separable_fixture_and_is_reproducible():
    model = RandomForestClassifier.fit(dataset(), n_trees=15, max_depth=3, max_features=1, seed=7)
    repeat = RandomForestClassifier.fit(dataset(), n_trees=15, max_depth=3, max_features=1, seed=7)
    assert model == repeat
    assert model.predict((Decimal("1.5"), Decimal("0"))) == "bull"
    assert model.predict((Decimal("9.5"), Decimal("0"))) == "bear"
    assert model.predict_many(((Decimal("1.5"), Decimal("0")),)) == ("bull",)


def test_random_forest_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="n_trees"):
        RandomForestClassifier.fit(dataset(), n_trees=0)
    with pytest.raises(ValueError, match="max_depth"):
        RandomForestClassifier.fit(dataset(), max_depth=0)
    with pytest.raises(ValueError, match="min_samples_split"):
        RandomForestClassifier.fit(dataset(), min_samples_split=1)
    with pytest.raises(ValueError, match="max_features"):
        RandomForestClassifier.fit(dataset(), max_features=3)


def test_random_forest_requires_two_classes():
    data = FeatureDataset(features=((Decimal("1"),), (Decimal("2"),)), labels=("bull", "bull"))
    with pytest.raises(ValueError, match="two distinct labels"):
        RandomForestClassifier.fit(data)


def test_random_forest_predict_rejects_wrong_width():
    model = RandomForestClassifier.fit(dataset(), n_trees=5, seed=3)
    with pytest.raises(ValueError, match="feature width"):
        model.predict((Decimal("1"),))
