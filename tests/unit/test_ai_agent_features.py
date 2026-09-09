from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from packages.ai_agent.features import FeatureRequest, calculate_features
from packages.market_data.models import Candle


def _candles() -> list[Candle]:
    start = datetime(2026, 1, 2, 9, 15)
    return [
        Candle(start + timedelta(minutes=5 * i), "NIFTY", "5m", Decimal(100 + i), Decimal(101 + i), Decimal(99 + i), Decimal(100 + i), Decimal(1000))
        for i in range(4)
    ]


def test_calculate_selected_features_is_candle_aligned() -> None:
    result = calculate_features(_candles(), FeatureRequest(("EMA", "VWAP"), ema_period=2))

    assert len(result.rows) == 4
    assert result.rows[0].timestamp == _candles()[0].timestamp
    assert result.rows[0].as_mapping()["ema"] is None
    assert result.rows[1].as_mapping()["ema"] == Decimal("100.5")
    assert result.rows[0].as_mapping()["vwap"] == Decimal("100")
    assert result.rows[3].as_mapping()["vwap"] == Decimal("101.5")


def test_atr_is_available_with_explicit_period() -> None:
    result = calculate_features(_candles(), FeatureRequest(("atr",), atr_period=2))

    assert result.rows[0].as_mapping()["atr"] is None
    assert result.rows[1].as_mapping()["atr"] == Decimal("2")


def test_unsupported_feature_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported features"):
        FeatureRequest(("rsi",))


def test_invalid_candle_order_fails_closed() -> None:
    candles = _candles()
    candles[2] = Candle(candles[1].timestamp, "NIFTY", "5m", Decimal(102), Decimal(103), Decimal(101), Decimal(102), Decimal(1000))

    with pytest.raises(ValueError, match="strictly increasing"):
        calculate_features(candles, FeatureRequest(("ema",)))


def test_invalid_ohlc_fails_closed() -> None:
    candles = _candles()
    candles[0] = Candle(candles[0].timestamp, "NIFTY", "5m", Decimal(100), Decimal(99), Decimal(100), Decimal(100), Decimal(1000))

    with pytest.raises(ValueError, match="high must be >= low"):
        calculate_features(candles, FeatureRequest(("vwap",)))


def test_feature_result_is_deterministic() -> None:
    request = FeatureRequest(("ema", "atr", "vwap"), ema_period=3, atr_period=3)

    assert calculate_features(_candles(), request) == calculate_features(_candles(), request)
