from decimal import Decimal

import pytest

from packages.backtest.events import Trade
from packages.portfolio.portfolio import Portfolio


def trade(entry_index: int, exit_index: int, pnl: str) -> Trade:
    return Trade(
        entry_index=entry_index,
        exit_index=exit_index,
        direction="bullish",
        entry=Decimal("100"),
        exit=Decimal("101"),
        quantity=Decimal("1"),
        gross_pnl=Decimal(pnl),
        costs=Decimal("0"),
        net_pnl=Decimal(pnl),
    )


def test_portfolio_records_realized_pnl_and_curve() -> None:
    portfolio = Portfolio(Decimal("100000"))
    assert portfolio.record_trade(trade(2, 5, "10")) == Decimal("100010")
    portfolio.record_trade(trade(6, 9, "-4"))

    assert portfolio.realized_pnl == Decimal("6")
    assert portfolio.equity == Decimal("100006")
    assert portfolio.realized_equity_curve() == [
        (5, Decimal("100010")),
        (9, Decimal("100006")),
    ]


def test_record_trades_orders_by_exit_index() -> None:
    portfolio = Portfolio(Decimal("100000"))
    portfolio.record_trades([trade(5, 9, "2"), trade(1, 3, "7")])
    assert portfolio.trades[0].exit_index == 3
    assert portfolio.realized_equity_curve() == [
        (3, Decimal("100007")),
        (9, Decimal("100009")),
    ]


def test_portfolio_rejects_non_positive_cash() -> None:
    with pytest.raises(ValueError, match="cash must be positive"):
        Portfolio(Decimal("0"))
