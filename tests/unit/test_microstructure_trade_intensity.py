from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from packages.microstructure.trade_flow import TradePrint
from packages.microstructure.trade_intensity import trade_count, trade_intensity


def trade(quantity: str = "1") -> TradePrint:
    return TradePrint(Decimal("100"), Decimal(quantity), "buy")


def test_trade_count_counts_supplied_prints_only():
    assert trade_count([trade(), trade("2"), trade("3")]) == 3


def test_trade_intensity_is_count_per_second():
    start = datetime(2026, 1, 1, 9, 15, 0)
    end = start + timedelta(seconds=10)
    assert trade_intensity([trade(), trade("2"), trade("3"), trade()], start, end) == Decimal("0.4")


def test_trade_intensity_does_not_infer_missing_timestamps():
    start = datetime(2026, 1, 1, 9, 15, 0)
    end = start + timedelta(minutes=1)
    assert trade_intensity([], start, end) == Decimal("0")


def test_invalid_window_fails_closed():
    start = datetime(2026, 1, 1, 9, 15, 0)
    with pytest.raises(ValueError, match="after"):
        trade_intensity([trade()], start, start)
