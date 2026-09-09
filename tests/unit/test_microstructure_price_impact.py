from decimal import Decimal

import pytest

from packages.microstructure.price_impact import (
    implementation_shortfall,
    signed_notional,
    volume_weighted_average_price,
)
from packages.microstructure.trade_flow import TradePrint


def test_signed_notional_uses_explicit_trade_side():
    trades = (
        TradePrint(Decimal("100"), Decimal("2"), "buy"),
        TradePrint(Decimal("101"), Decimal("1"), "sell"),
    )
    assert signed_notional(trades) == Decimal("99")


def test_vwap_is_quantity_weighted():
    trades = (
        TradePrint(Decimal("100"), Decimal("2"), "buy"),
        TradePrint(Decimal("110"), Decimal("1"), "buy"),
    )
    assert volume_weighted_average_price(trades) == Decimal("310") / Decimal("3")


def test_implementation_shortfall_is_execution_vwap_minus_arrival():
    trades = (
        TradePrint(Decimal("101"), Decimal("2"), "buy"),
        TradePrint(Decimal("103"), Decimal("1"), "buy"),
    )
    assert implementation_shortfall(trades, Decimal("100")) == Decimal("5") / Decimal("3")


def test_zero_quantity_vwap_fails_closed():
    with pytest.raises(ValueError, match="zero"):
        volume_weighted_average_price(
            [TradePrint(Decimal("100"), Decimal("0"), "buy")]
        )


def test_non_positive_arrival_price_fails_closed():
    with pytest.raises(ValueError, match="arrival_price"):
        implementation_shortfall([], Decimal("0"))
