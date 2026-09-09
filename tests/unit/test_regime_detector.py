from decimal import Decimal

import pytest

from packages.regime.detector import RegimeThresholds, detect_regime
from packages.regime.features import RegimeFeatureVector


THRESHOLDS = RegimeThresholds(
    low_volatility_mean_abs_return=Decimal("0.005"),
    high_volatility_mean_abs_return=Decimal("0.03"),
    trending_return=Decimal("0.01"),
    trending_efficiency=Decimal("0.7"),
)


def features(
    period_return: str,
    mean_abs_return: str,
    efficiency: str,
) -> RegimeFeatureVector:
    return RegimeFeatureVector(
        period_return=Decimal(period_return),
        mean_absolute_return=Decimal(mean_abs_return),
        trend_slope=Decimal("1"),
        range_efficiency=Decimal(efficiency),
        average_volume=Decimal("100"),
    )


def test_positive_efficient_move_is_bull():
    assert detect_regime(features("0.02", "0.01", "0.8"), THRESHOLDS) == "bull"


def test_negative_efficient_move_is_bear():
    assert detect_regime(features("-0.02", "0.01", "0.8"), THRESHOLDS) == "bear"


def test_high_volatility_has_priority():
    assert detect_regime(features("0.02", "0.04", "0.9"), THRESHOLDS) == "high_volatility"


def test_low_volatility_has_priority():
    assert detect_regime(features("0.02", "0.002", "0.9"), THRESHOLDS) == "low_volatility"


def test_inefficient_move_is_range():
    assert detect_regime(features("0.02", "0.01", "0.4"), THRESHOLDS) == "range"


def test_thresholds_are_explicit_and_validated():
    with pytest.raises(ValueError, match="must not exceed"):
        RegimeThresholds(
            low_volatility_mean_abs_return=Decimal("0.04"),
            high_volatility_mean_abs_return=Decimal("0.03"),
            trending_return=Decimal("0.01"),
            trending_efficiency=Decimal("0.7"),
        )

    with pytest.raises(ValueError, match="must not exceed one"):
        RegimeThresholds(
            low_volatility_mean_abs_return=Decimal("0.005"),
            high_volatility_mean_abs_return=Decimal("0.03"),
            trending_return=Decimal("0.01"),
            trending_efficiency=Decimal("1.1"),
        )
