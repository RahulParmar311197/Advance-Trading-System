from decimal import Decimal

import pytest

from packages.regime.classifier import classify_regime
from packages.regime.detector import RegimeThresholds
from packages.regime.features import RegimeFeatureVector


def thresholds() -> RegimeThresholds:
    return RegimeThresholds(
        low_volatility_mean_abs_return=Decimal("0.01"),
        high_volatility_mean_abs_return=Decimal("0.05"),
        trending_return=Decimal("0.02"),
        trending_efficiency=Decimal("0.60"),
    )


def test_classifier_preserves_bull_primary_regime_and_labels():
    result = classify_regime(
        RegimeFeatureVector(
            period_return=Decimal("0.08"),
            mean_absolute_return=Decimal("0.03"),
            trend_slope=Decimal("2"),
            range_efficiency=Decimal("0.80"),
            average_volume=Decimal("1000"),
        ),
        thresholds(),
    )
    assert result.regime == "bull"
    assert result.trend_direction == "up"
    assert result.volatility_state == "normal"


def test_classifier_labels_bear_and_high_volatility():
    result = classify_regime(
        RegimeFeatureVector(
            period_return=Decimal("-0.08"),
            mean_absolute_return=Decimal("0.06"),
            trend_slope=Decimal("-2"),
            range_efficiency=Decimal("0.80"),
            average_volume=Decimal("1000"),
        ),
        thresholds(),
    )
    assert result.regime == "high_volatility"
    assert result.trend_direction == "down"
    assert result.volatility_state == "high"


def test_classifier_labels_range_and_low_volatility():
    result = classify_regime(
        RegimeFeatureVector(
            period_return=Decimal("0.01"),
            mean_absolute_return=Decimal("0.005"),
            trend_slope=Decimal("0.1"),
            range_efficiency=Decimal("0.30"),
            average_volume=Decimal("1000"),
        ),
        thresholds(),
    )
    assert result.regime == "low_volatility"
    assert result.trend_direction == "neutral"
    assert result.volatility_state == "low"


def test_classifier_is_immutable():
    result = classify_regime(
        RegimeFeatureVector(
            period_return=Decimal("0.03"),
            mean_absolute_return=Decimal("0.03"),
            trend_slope=Decimal("1"),
            range_efficiency=Decimal("0.70"),
            average_volume=Decimal("1000"),
        ),
        thresholds(),
    )
    with pytest.raises(AttributeError):
        result.regime = "bear"
