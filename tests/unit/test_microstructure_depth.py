from decimal import Decimal

import pytest

from packages.microstructure.depth import (
    DepthLevel,
    OrderBookDepth,
    depth_within_ticks,
    total_depth,
)


def level(price: str, quantity: str) -> DepthLevel:
    return DepthLevel(Decimal(price), Decimal(quantity))


def test_order_book_validates_and_exposes_best_levels() -> None:
    book = OrderBookDepth.from_levels(
        [level("99", "10"), level("98", "20")],
        [level("101", "7"), level("102", "13")],
    )
    assert book.best_bid == level("99", "10")
    assert book.best_ask == level("101", "7")


def test_total_depth_sums_only_supplied_levels() -> None:
    assert total_depth([level("99", "10"), level("98", "2.5")]) == Decimal("12.5")


def test_depth_within_ticks_uses_absolute_price_distance() -> None:
    levels = [level("99", "10"), level("100", "4"), level("102", "8")]
    assert depth_within_ticks(levels, Decimal("100"), 1) == Decimal("14")


def test_duplicate_price_level_fails_closed() -> None:
    with pytest.raises(ValueError, match="duplicate bid price level"):
        OrderBookDepth.from_levels(
            [level("99", "1"), level("99", "2")],
            [level("101", "1")],
        )


def test_unsorted_bid_levels_fail_closed() -> None:
    with pytest.raises(ValueError, match="strictly descending"):
        OrderBookDepth.from_levels(
            [level("98", "1"), level("99", "1")],
            [level("101", "1")],
        )


def test_crossed_book_fails_closed() -> None:
    with pytest.raises(ValueError, match="best bid must be below best ask"):
        OrderBookDepth.from_levels([level("101", "1")], [level("101", "2")])


def test_invalid_depth_query_fails_closed() -> None:
    with pytest.raises(ValueError, match="ticks"):
        depth_within_ticks([level("100", "1")], Decimal("100"), -1)
