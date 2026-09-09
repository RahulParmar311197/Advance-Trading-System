from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset, build_regime_feature_dataset
from packages.regime.detector import Regime
from packages.regime.features import RegimeFeatureVector


def feature_vector() -> RegimeFeatureVector:
    return RegimeFeatureVector(
        period_return=Decimal("0.02"),
        mean_absolute_return=Decimal("0.01"),
        trend_slope=Decimal("1.5"),
        range_efficiency=Decimal("0.8"),
        average_volume=Decimal("1000"),
    )


def test_dataset_preserves_explicit_labels_and_feature_order():
    rows = ((feature_vector(), "bull"), (feature_vector(), "bear"))
    dataset = build_regime_feature_dataset(rows)
    assert isinstance(dataset, FeatureDataset)
    assert dataset.labels == ("bull", "bear")
    assert dataset.features[0] == (
        Decimal("0.02"), Decimal("0.01"), Decimal("1.5"), Decimal("0.8"), Decimal("1000")
    )


def test_empty_rows_fail_closed():
    with pytest.raises(ValueError, match="rows"):
        build_regime_feature_dataset(())


def test_dataset_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal length"):
        FeatureDataset(features=((Decimal("1"),),), labels=())


def test_dataset_rejects_inconsistent_feature_width():
    with pytest.raises(ValueError, match="equal width"):
        FeatureDataset(
            features=((Decimal("1"),), (Decimal("1"), Decimal("2"))),
            labels=("bull", "bear"),
        )
