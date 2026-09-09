from decimal import Decimal

import pytest

from packages.backtest.broker_simulator import BrokerSimulator
from packages.backtest.events import Trade
from packages.backtest.portfolio import ending_equity, realized_equity_curve
from packages.portfolio.correlation import correlation_matrix, pearson_correlation
from packages.portfolio.exposure import aggregate_exposure, total_exposure


def trade(exit_index, net_pnl):
    return Trade(0, exit_index, "bullish", Decimal("100"), Decimal("101"), Decimal("1"), net_pnl, Decimal("0"), net_pnl)


def test_realized_equity_curve_is_ordered_by_exit_candle():
    trades = [trade(5, Decimal("20")), trade(3, Decimal("-10"))]
    assert realized_equity_curve(Decimal("100000"), trades) == [(3, Decimal("99990")), (5, Decimal("100010"))]
    assert ending_equity(Decimal("100000"), trades) == Decimal("100010")


def test_exposure_aggregates_by_symbol():
    positions = [
        {"symbol": "NIFTY", "quantity": "2", "price": "100"},
        {"symbol": "NIFTY", "quantity": "1", "price": "50"},
        {"symbol": "BANKNIFTY", "quantity": "1", "price": "200"},
    ]
    assert aggregate_exposure(positions) == {"NIFTY": Decimal("250"), "BANKNIFTY": Decimal("200")}
    assert total_exposure(positions) == Decimal("450")


def test_correlation_matrix_is_symmetric():
    series = {"a": [1, 2, 3], "b": [1, 2, 4]}
    matrix = correlation_matrix(series)
    assert matrix["a"]["a"] == Decimal("1")
    assert matrix["a"]["b"] == matrix["b"]["a"]
    assert pearson_correlation([1, 2, 3], [1, 2, 4]) > Decimal("0")


def test_broker_simulator_applies_slippage_and_commission():
    fill = BrokerSimulator(Decimal("10")).fill("buy", Decimal("100"), Decimal("2"))
    assert fill.filled_price > fill.requested_price
    assert fill.commission > Decimal("0")


@pytest.mark.parametrize("side", ["hold", "BUY"])
def test_broker_simulator_rejects_invalid_side(side):
    with pytest.raises(ValueError):
        BrokerSimulator().fill(side, Decimal("100"), Decimal("1"))
