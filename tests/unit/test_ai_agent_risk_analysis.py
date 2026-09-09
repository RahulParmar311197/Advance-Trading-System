from decimal import Decimal

import pytest

from packages.ai_agent.backtest import BacktestRequest, BacktestResult
from packages.ai_agent.risk_analysis import RiskAnalysisRequest, analyze_risk
from packages.backtest.events import Trade


def _result(*pnl: str, capital: str = "100000") -> BacktestResult:
    trades = tuple(
        Trade(
            entry_index=i * 2,
            exit_index=i * 2 + 1,
            direction="bullish",
            entry=Decimal("100"),
            exit=Decimal("100"),
            quantity=Decimal("1"),
            gross_pnl=Decimal(value),
            costs=Decimal("0"),
            net_pnl=Decimal(value),
        )
        for i, value in enumerate(pnl)
    )
    return BacktestResult(
        request=BacktestRequest("Liquidity MSS FVG", capital=Decimal(capital)),
        trades=trades,
        metrics={},
        equity_curve=(),
    )


def test_risk_analysis_measures_realized_losses_and_approves_within_limits():
    result = analyze_risk(_result("1000", "-500", "1000"))

    assert result.approved
    assert result.breaches == ()
    assert result.metrics["trade_count"] == 3
    assert result.metrics["worst_trade_loss"] == Decimal("0.005")
    assert result.metrics["max_loss_streak"] == 1


def test_risk_analysis_rejects_drawdown_loss_streak_position_and_cost_breaches():
    result = analyze_risk(
        _result("-3000", "-3000", "-3000", capital="10000"),
        RiskAnalysisRequest(
            max_drawdown=Decimal("0.10"),
            max_single_trade_loss=Decimal("0.20"),
            max_loss_streak=2,
            max_position_value=Decimal("50"),
            max_cost_fraction=Decimal("0"),
        ),
    )

    assert not result.approved
    assert "maximum drawdown exceeded" in result.breaches
    assert "maximum loss streak exceeded" in result.breaches
    assert "maximum position value exceeded" in result.breaches


def test_risk_request_validates_thresholds():
    with pytest.raises(ValueError, match="max_drawdown"):
        RiskAnalysisRequest(max_drawdown=Decimal("1.1"))
    with pytest.raises(ValueError, match="max_loss_streak"):
        RiskAnalysisRequest(max_loss_streak=0)
    with pytest.raises(ValueError, match="max_position_value"):
        RiskAnalysisRequest(max_position_value=Decimal("0"))
