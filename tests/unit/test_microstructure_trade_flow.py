from decimal import Decimal

import pytest

from packages.microstructure.trade_flow import (
    TradePrint,
    signed_trade_volume,
    trade_flow_imbalance,
)


def trade(price: str, quantity: str, side: str) -> TradePrint:
    return TradePrint(Decimal(price), Decimal(quantity), side)


def test_signed_trade_volume_uses_explicit_aggressor_side():
    assert signed_trade_volume(
        [trade("100", "7", "buy"), trade("101", "3", "sell")]
    ) == Decimal("4")


def test_trade_flow_imbalance_is_normalized():
    assert trade_flow_imbalance(
        [trade("100", "75", "buy"), trade("100", "25", "sell")]
    ) == Decimal("0.5")


def test_zero_trade_volume_fails_closed():
    with pytest.raises(ValueError, match="total quantity"):
        trade_flow_imbalance([])


def test_invalid_side_fails_closed():
    with pytest.raises(ValueError, match="side"):
        trade("100", "1", "unknown")


def test_negative_quantity_fails_closed():
    with pytest.raises(ValueError, match="non-negative"):
        trade("100", "-1", "buy")
