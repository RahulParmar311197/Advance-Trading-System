from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide, OrderStatus, OrderType
from packages.execution.paper_broker import PaperBroker, PaperFill


NOW = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)


def test_market_order_fills_only_from_explicit_observation() -> None:
    broker = PaperBroker()
    order = broker.submit_order(
        OrderRequest(symbol="NIFTY", side=OrderSide.BUY, quantity=Decimal("2"))
    )
    assert order.status is OrderStatus.ACCEPTED
    filled = broker.process_fill(order.order_id, PaperFill("NIFTY", Decimal("25000"), NOW))
    assert filled.status is OrderStatus.FILLED
    assert filled.filled_quantity == Decimal("2")
    assert filled.average_fill_price == Decimal("25000")


def test_partial_fills_accumulate_with_weighted_average_price() -> None:
    broker = PaperBroker()
    order = broker.submit_order(
        OrderRequest(symbol="NIFTY", side=OrderSide.BUY, quantity=Decimal("2"))
    )
    partial = broker.process_fill(
        order.order_id,
        PaperFill("NIFTY", Decimal("100"), NOW, quantity=Decimal("0.5")),
    )
    assert partial.status is OrderStatus.PARTIALLY_FILLED
    assert partial.filled_quantity == Decimal("0.5")
    assert partial.average_fill_price == Decimal("100")

    filled = broker.process_fill(
        order.order_id,
        PaperFill("NIFTY", Decimal("102"), NOW, quantity=Decimal("1.5")),
    )
    assert filled.status is OrderStatus.FILLED
    assert filled.filled_quantity == Decimal("2")
    assert filled.average_fill_price == Decimal("101.5")


def test_fill_cannot_exceed_remaining_quantity() -> None:
    broker = PaperBroker()
    order = broker.submit_order(
        OrderRequest(symbol="NIFTY", side=OrderSide.BUY, quantity=Decimal("1"))
    )
    with pytest.raises(ValueError, match="exceeds remaining"):
        broker.process_fill(
            order.order_id,
            PaperFill("NIFTY", Decimal("100"), NOW, quantity=Decimal("1.1")),
        )


def test_limit_order_waits_until_limit_is_reached() -> None:
    broker = PaperBroker()
    order = broker.submit_order(
        OrderRequest(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=Decimal("1"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("100"),
        )
    )
    pending = broker.process_fill(order.order_id, PaperFill("NIFTY", Decimal("101"), NOW))
    assert pending.status is OrderStatus.ACCEPTED
    filled = broker.process_fill(order.order_id, PaperFill("NIFTY", Decimal("99"), NOW))
    assert filled.status is OrderStatus.FILLED


def test_symbol_mismatch_and_cancel_are_fail_closed() -> None:
    broker = PaperBroker()
    order = broker.submit_order(
        OrderRequest(symbol="NIFTY", side=OrderSide.SELL, quantity=Decimal("1"))
    )
    with pytest.raises(ValueError, match="fill symbol"):
        broker.process_fill(order.order_id, PaperFill("BANKNIFTY", Decimal("50000"), NOW))
    canceled = broker.cancel_order(order.order_id)
    assert canceled.status is OrderStatus.CANCELED
    with pytest.raises(ValueError, match="cannot be canceled"):
        broker.cancel_order(order.order_id)


def test_fill_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        PaperFill("NIFTY", Decimal("100"), datetime(2026, 1, 2, 9, 15))


def test_fill_quantity_requires_positive_value() -> None:
    with pytest.raises(ValueError, match="fill quantity must be positive"):
        PaperFill("NIFTY", Decimal("100"), NOW, quantity=Decimal("0"))
