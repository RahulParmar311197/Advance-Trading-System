from decimal import Decimal

import pytest

from packages.microstructure.imbalance import bid_ask_imbalance, depth_imbalance


def test_bid_ask_imbalance_is_normalized():
    assert bid_ask_imbalance(Decimal("75"), Decimal("25")) == Decimal("0.5")
    assert bid_ask_imbalance(Decimal("25"), Decimal("75")) == Decimal("-0.5")


def test_depth_imbalance_uses_only_supplied_visible_quantities():
    assert depth_imbalance(
        (Decimal("60"), Decimal("20")),
        (Decimal("40"), Decimal("20")),
    ) == Decimal("1") / Decimal("7")


def test_zero_total_quantity_fails_closed():
    with pytest.raises(ValueError, match="total quantity"):
        bid_ask_imbalance(Decimal("0"), Decimal("0"))


def test_negative_quantity_fails_closed():
    with pytest.raises(ValueError, match="non-negative"):
        bid_ask_imbalance(Decimal("-1"), Decimal("2"))
