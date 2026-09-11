from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide, OrderType
from packages.execution.execution_simulator import ExecutionObservation, simulate_fill
from packages.market_data.models import Candle


NOW = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)


def candle(*, open: str, high: str, low: str, close: str, symbol: str = "NIFTY") -> Candle:
    return Candle(
        timestamp=NOW,
        symbol=symbol,
        timeframe="5m",
        open=Decimal(open),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal("100"),
    )


def test_market_buy_uses_supplied_open_and_explicit_slippage() -> None:
    request = OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"))
    fill = simulate_fill(
        request,
        ExecutionObservation(candle(open="100", high="105", low="99", close="104")),
        slippage_bps=Decimal("10"),
    )
    assert fill is not None
    assert fill.price == Decimal("100.1")
    assert fill.timestamp == NOW


def test_limit_order_fills_only_when_candle_crosses_limit() -> None:
    request = OrderRequest(
        "NIFTY",
        OrderSide.BUY,
        Decimal("1"),
        order_type=OrderType.LIMIT,
        limit_price=Decimal("100"),
    )
    assert simulate_fill(
        request,
        ExecutionObservation(candle(open="102", high="104", low="101", close="103")),
    ) is None
    fill = simulate_fill(
        request,
        ExecutionObservation(candle(open="102", high="104", low="99", close="101")),
        slippage_bps=Decimal("100"),
    )
    assert fill is not None
    assert fill.price == Decimal("100")


def test_stop_sell_models_gap_and_slippage() -> None:
    request = OrderRequest(
        "NIFTY",
        OrderSide.SELL,
        Decimal("1"),
        order_type=OrderType.STOP,
        stop_price=Decimal("100"),
    )
    fill = simulate_fill(
        request,
        ExecutionObservation(candle(open="95", high="101", low="94", close="96")),
        slippage_bps=Decimal("100"),
    )
    assert fill is not None
    assert fill.price == Decimal("94.05")


def test_observation_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ExecutionObservation(
            Candle(
                timestamp=datetime(2026, 1, 2, 9, 15),
                symbol="NIFTY",
                timeframe="5m",
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                volume=Decimal("100"),
            )
        )


def test_observation_and_request_symbol_must_match() -> None:
    request = OrderRequest("BANKNIFTY", OrderSide.BUY, Decimal("1"))
    with pytest.raises(ValueError, match="does not match"):
        simulate_fill(
            request,
            ExecutionObservation(candle(open="100", high="101", low="99", close="100")),
        )


def test_invalid_slippage_is_rejected() -> None:
    request = OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"))
    with pytest.raises(ValueError, match="non-negative"):
        simulate_fill(
            request,
            ExecutionObservation(candle(open="100", high="101", low="99", close="100")),
            slippage_bps=Decimal("-1"),
        )


def test_paper_broker_can_apply_simulated_observation() -> None:
    from packages.execution.paper_broker import PaperBroker

    broker = PaperBroker()
    order = broker.submit_order(OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")))
    filled = broker.process_observation(
        order.order_id,
        ExecutionObservation(candle(open="100", high="101", low="99", close="100")),
        slippage_bps=Decimal("10"),
    )
    assert filled.status.value == "filled"
    assert filled.average_fill_price == Decimal("100.1")
