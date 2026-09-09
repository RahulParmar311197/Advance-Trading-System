from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from packages.market_data.models import Candle
from packages.regime.dataset import RegimeDatasetRow, build_regime_dataset
from packages.regime.detector import RegimeThresholds


def candle(index: int, close: str, volume: str = "100") -> Candle:
    return Candle(
        timestamp=datetime(2026, 1, 1) + timedelta(minutes=5 * index),
        symbol="NIFTY",
        timeframe="5m",
        open=Decimal(close),
        high=Decimal(close) + Decimal("1"),
        low=Decimal(close) - Decimal("1"),
        close=Decimal(close),
        volume=Decimal(volume),
    )


def thresholds() -> RegimeThresholds:
    return RegimeThresholds(
        low_volatility_mean_abs_return=Decimal("0.001"),
        high_volatility_mean_abs_return=Decimal("0.01"),
        trending_return=Decimal("0.005"),
        trending_efficiency=Decimal("0.5"),
    )


def test_dataset_rows_preserve_window_order_and_computed_features():
    windows = (
        (candle(0, "100"), candle(1, "101")),
        (candle(2, "101"), candle(3, "99")),
    )
    rows = build_regime_dataset(windows, thresholds())
    assert rows[0].observation_index == 0
    assert rows[1].observation_index == 1
    assert rows[0].features.period_return == Decimal("0.01")
    assert rows[0].classification.regime == "high_volatility"
    assert all(isinstance(row, RegimeDatasetRow) for row in rows)


def test_empty_windows_fail_closed():
    with pytest.raises(ValueError, match="windows"):
        build_regime_dataset((), thresholds())


def test_invalid_candle_window_fails_closed():
    with pytest.raises(ValueError, match="strictly increasing"):
        build_regime_dataset(
            ((candle(1, "100"), candle(0, "101")),), thresholds()
        )
