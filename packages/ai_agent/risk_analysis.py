from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from packages.ai_agent.backtest import BacktestResult


@dataclass(frozen=True, slots=True)
class RiskAnalysisRequest:
    """Explicit thresholds used to assess an existing backtest result."""

    max_drawdown: Decimal = Decimal("0.10")
    max_single_trade_loss: Decimal = Decimal("0.02")
    max_loss_streak: int = 5
    max_position_value: Decimal = Decimal("500000")
    max_cost_fraction: Decimal = Decimal("0.01")

    def __post_init__(self) -> None:
        if self.max_drawdown < 0 or self.max_drawdown > 1:
            raise ValueError("max_drawdown must be in [0, 1]")
        if self.max_single_trade_loss < 0 or self.max_single_trade_loss > 1:
            raise ValueError("max_single_trade_loss must be in [0, 1]")
        if self.max_loss_streak <= 0:
            raise ValueError("max_loss_streak must be positive")
        if self.max_position_value <= 0:
            raise ValueError("max_position_value must be positive")
        if self.max_cost_fraction < 0 or self.max_cost_fraction > 1:
            raise ValueError("max_cost_fraction must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class RiskAnalysisResult:
    """Measured risk observations and fail-closed threshold breaches."""

    metrics: Mapping[str, Decimal | int]
    breaches: tuple[str, ...]
    approved: bool


def analyze_risk(
    result: BacktestResult, request: RiskAnalysisRequest | None = None
) -> RiskAnalysisResult:
    """Analyze only realized risk in a supplied backtest; never alter its trades."""
    resolved = request or RiskAnalysisRequest()
    capital = result.request.capital
    trades = result.trades

    equity = capital
    peak = capital
    max_drawdown = Decimal("0")
    worst_loss = Decimal("0")
    max_position_value = Decimal("0")
    total_costs = Decimal("0")
    loss_streak = 0
    max_loss_streak = 0

    for trade in sorted(trades, key=lambda item: (item.exit_index, item.entry_index)):
        notional = abs(trade.entry * trade.quantity)
        max_position_value = max(max_position_value, notional)
        total_costs += trade.costs
        equity += trade.net_pnl
        peak = max(peak, equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - equity) / peak)
        if trade.net_pnl < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
            worst_loss = max(worst_loss, abs(trade.net_pnl) / capital)
        else:
            loss_streak = 0

    cost_fraction = total_costs / capital
    metrics: dict[str, Decimal | int] = {
        "trade_count": len(trades),
        "max_drawdown": max_drawdown,
        "worst_trade_loss": worst_loss,
        "max_loss_streak": max_loss_streak,
        "max_position_value": max_position_value,
        "cost_fraction": cost_fraction,
    }

    breaches: list[str] = []
    if max_drawdown > resolved.max_drawdown:
        breaches.append("maximum drawdown exceeded")
    if worst_loss > resolved.max_single_trade_loss:
        breaches.append("maximum single-trade loss exceeded")
    if max_loss_streak > resolved.max_loss_streak:
        breaches.append("maximum loss streak exceeded")
    if max_position_value > resolved.max_position_value:
        breaches.append("maximum position value exceeded")
    if cost_fraction > resolved.max_cost_fraction:
        breaches.append("maximum cost fraction exceeded")

    return RiskAnalysisResult(metrics=metrics, breaches=tuple(breaches), approved=not breaches)
