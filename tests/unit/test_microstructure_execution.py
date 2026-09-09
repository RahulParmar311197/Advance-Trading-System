from decimal import Decimal

import pytest

from packages.microstructure.depth import DepthLevel, OrderBookDepth
from packages.microstructure.execution import ExecutionFill, execute_market_order


def book() -> OrderBookDepth:
    return OrderBookDepth.from_levels(
        bids=(DepthLevel(Decimal("99"), Decimal("3")), DepthLevel(Decimal("98"), Decimal("4"))),
        asks=(DepthLevel(Decimal("101"), Decimal("2")), DepthLevel(Decimal("102"), Decimal("5"))),
    )


def test_buy_consumes_best_asks_then_next_level():
    result = execute_market_order(book(), "buy", Decimal("4"))
    assert result.filled_quantity == Decimal("4")
    assert result.unfilled_quantity == Decimal("0")
    assert result.notional == Decimal("406")
    assert result.average_price == Decimal("406") / Decimal("4")
    assert result.fills == (
        ExecutionFill(Decimal("101"), Decimal("2")),
        ExecutionFill(Decimal("102"), Decimal("2")),
    )


def test_sell_consumes_best_bids_then_next_level():
    result = execute_market_order(book(), "sell", Decimal("5"))
    assert result.filled_quantity == Decimal("5")
    assert result.unfilled_quantity == Decimal("0")
    assert result.notional == Decimal("493")
    assert result.average_price == Decimal("493") / Decimal("5")


def test_insufficient_visible_depth_returns_partial_fill():
    result = execute_market_order(book(), "buy", Decimal("10"))
    assert result.filled_quantity == Decimal("7")
    assert result.unfilled_quantity == Decimal("3")
    assert result.average_price == Decimal("712") / Decimal("7")


def test_invalid_side_fails_closed():
    with pytest.raises(ValueError, match="side"):
        execute_market_order(book(), "hold", Decimal("1"))  # type: ignore[arg-type]


def test_non_positive_quantity_fails_closed():
    with pytest.raises(ValueError, match="quantity"):
        execute_market_order(book(), "buy", Decimal("0"))
