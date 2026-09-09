from decimal import Decimal

import pytest

from packages.microstructure.depth import DepthLevel, OrderBookDepth
from packages.microstructure.liquidity import (
    LiquiditySnapshot,
    depth_recovery_ratio,
    spread_recovery_ratio,
    visible_liquidity,
)
from packages.microstructure.spread import BidAskQuote


def book() -> OrderBookDepth:
    return OrderBookDepth.from_levels(
        [DepthLevel(Decimal("99"), Decimal("10")), DepthLevel(Decimal("98"), Decimal("5"))],
        [DepthLevel(Decimal("101"), Decimal("8")), DepthLevel(Decimal("102"), Decimal("4"))],
    )


def test_visible_liquidity_sums_both_sides():
    assert visible_liquidity(book()) == Decimal("27")


def test_snapshot_exposes_depth_and_spread_metrics():
    snapshot = LiquiditySnapshot(
        quote=BidAskQuote(Decimal("99"), Decimal("101")),
        depth=book(),
    )
    assert snapshot.visible_depth == Decimal("27")
    assert snapshot.spread == Decimal("2")
    assert snapshot.relative_spread == Decimal("2") / Decimal("100")


def test_depth_recovery_ratio():
    assert depth_recovery_ratio(Decimal("100"), Decimal("40"), Decimal("70")) == Decimal("0.5")


def test_depth_recovery_can_exceed_one_without_clamping():
    assert depth_recovery_ratio(Decimal("100"), Decimal("40"), Decimal("120")) == Decimal("4") / Decimal("3")


def test_depth_recovery_requires_real_depletion():
    with pytest.raises(ValueError, match="depletion"):
        depth_recovery_ratio(Decimal("100"), Decimal("100"), Decimal("100"))


def test_depth_recovery_rejects_invalid_ordering():
    with pytest.raises(ValueError, match="stressed_depth"):
        depth_recovery_ratio(Decimal("40"), Decimal("50"), Decimal("60"))
    with pytest.raises(ValueError, match="recovered_depth"):
        depth_recovery_ratio(Decimal("100"), Decimal("40"), Decimal("30"))


def test_spread_recovery_ratio():
    assert spread_recovery_ratio(Decimal("1"), Decimal("3"), Decimal("2")) == Decimal("0.5")


def test_spread_recovery_rejects_invalid_ordering_and_zero_widening():
    with pytest.raises(ValueError, match="widening"):
        spread_recovery_ratio(Decimal("2"), Decimal("2"), Decimal("2"))
    with pytest.raises(ValueError, match="stressed_spread"):
        spread_recovery_ratio(Decimal("3"), Decimal("2"), Decimal("1"))
    with pytest.raises(ValueError, match="recovered_spread"):
        spread_recovery_ratio(Decimal("1"), Decimal("3"), Decimal("4"))
