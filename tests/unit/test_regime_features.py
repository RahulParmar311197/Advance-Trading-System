from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from packages.market_data.models import Candle
from packages.regime.features import calculate_regime_features


def candles():
    start = datetime(2026, 1, 1, 9, 15)
    return (
        Candle(start, "NIFTY", "5m", Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"), Decimal("10")),
        Candle(start + timedelta(minutes=5), "NIFTY", "5m", Decimal("101"), Decimal("104"), Decimal("100"), Decimal("103"), Decimal("20")),
        Candle(start + timedelta(minutes=10), "NIFTY", "5m", Decimal("103"), Decimal("105"), Decimal("102"), Decimal("104"), Decimal("30")),
    )


def test_regime_features_are_deterministic():
    features = calculate_regime_features(candles())
    path = Decimal("4") / Decimal("100")
    assert features.period_return == Decimal("4") / Decimal("101")
    assert features.mean_absolute_return == (Decimal("2") / Decimal("101") + Decimal("1") / Decimal("103")) / Decimal("2")
    assert features.trend_slope == Decimal("1.5")
    assert features.range_efficiency == (Decimal("4") / Decimal("101")) / path
    assert Decimal("0") <= features.range_efficiency <= Decimal("1")
    assert features.average_volume == Decimal("20")


def test_single_candle_window_has_zero_change_features():
    single = (candles()[0],)
    features = calculate_regime_features(single)
    assert features.period_return == Decimal("0")
    assert features.mean_absolute_return == Decimal("0")
    assert features.trend_slope == Decimal("0")
    assert features.range_efficiency == Decimal("0")
    assert features.average_volume == Decimal("10")


def test_empty_window_fails_closed():
    with pytest.raises(ValueError, match="empty"):
        calculate_regime_features(())


def test_non_increasing_timestamps_fail_closed():
    values = list(candles())
    values[1] = Candle(values[0].timestamp, "NIFTY", "5m", Decimal("101"), Decimal("104"), Decimal("100"), Decimal("103"), Decimal("20"))
    with pytest.raises(ValueError, match="timestamp"):
        calculate_regime_features(values)


def test_mixed_symbol_or_timeframe_fails_closed():
    values = list(candles())
    values[1] = Candle(values[1].timestamp, "BANKNIFTY", "5m", values[1].open, values[1].high, values[1].low, values[1].close, values[1].volume)
    with pytest.raises(ValueError, match="symbol and timeframe"):
        calculate_regime_features(values)


def test_invalid_close_or_volume_fails_closed():
    values = list(candles())
    values[1] = Candle(values[1].timestamp, "NIFTY", "5m", Decimal("101"), Decimal("104"), Decimal("100"), Decimal("0"), Decimal("20"))
    with pytest.raises(ValueError, match="close"):
        calculate_regime_features(values)

    values[1] = Candle(values[1].timestamp, "NIFTY", "5m", Decimal("101"), Decimal("104"), Decimal("100"), Decimal("103"), Decimal("-1"))
    with pytest.raises(ValueError, match="volume"):
        calculate_regime_features(values)
