from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.backtest import BacktestRequest, run_backtest_tool
from packages.market_data.models import Candle


def _candles() -> list[Candle]:
    start = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    values = [
        (100, 102, 99, 101),
        (101, 103, 100, 102),
        (102, 106, 101, 105),
        (105, 107, 104, 106),
        (106, 108, 105, 107),
        (107, 109, 106, 108),
        (108, 110, 107, 109),
    ]
    return [
        Candle(
            start + timedelta(minutes=5 * i),
            "NIFTY",
            "5m",
            Decimal(open_),
            Decimal(high),
            Decimal(low),
            Decimal(close),
            Decimal("1000"),
        )
        for i, (open_, high, low, close) in enumerate(values)
    ]


def test_backtest_tool_runs_registered_strategy_without_synthesizing_trades() -> None:
    result = run_backtest_tool(
        _candles(),
        BacktestRequest("Liquidity MSS FVG", slippage_bps=Decimal("1")),
    )

    assert result.trades == ()
    assert result.metrics["trade_count"] == 0
    assert result.metrics["total_return"] == Decimal("0")
    assert result.equity_curve == ((0, Decimal("100000")),)


def test_backtest_tool_is_deterministic() -> None:
    request = BacktestRequest("Liquidity MSS FVG", capital=Decimal("50000"))

    assert run_backtest_tool(_candles(), request) == run_backtest_tool(_candles(), request)


def test_backtest_tool_fails_closed_for_unknown_strategy() -> None:
    with pytest.raises(ValueError, match="unknown strategy"):
        run_backtest_tool(_candles(), BacktestRequest("missing"))


def test_backtest_request_validates_cost_and_capital_inputs() -> None:
    with pytest.raises(ValueError, match="capital"):
        BacktestRequest("Liquidity MSS FVG", capital=Decimal("0"))
    with pytest.raises(ValueError, match="risk_per_trade"):
        BacktestRequest("Liquidity MSS FVG", risk_per_trade=Decimal("1.1"))
    with pytest.raises(ValueError, match="slippage_bps"):
        BacktestRequest("Liquidity MSS FVG", slippage_bps=Decimal("-1"))


def test_backtest_tool_rejects_invalid_candle_order() -> None:
    candles = _candles()
    candles[2] = Candle(
        candles[1].timestamp,
        "NIFTY",
        "5m",
        Decimal("102"),
        Decimal("103"),
        Decimal("101"),
        Decimal("102"),
        Decimal("1000"),
    )

    with pytest.raises(ValueError, match="strictly increasing"):
        run_backtest_tool(candles, BacktestRequest("Liquidity MSS FVG"))
