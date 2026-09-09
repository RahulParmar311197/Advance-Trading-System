from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

from packages.backtest.events import Trade


@dataclass(slots=True)
class Portfolio:
    """Deterministic realized portfolio accounting for completed trades."""

    cash: Decimal
    realized_pnl: Decimal = Decimal("0")
    trades: list[Trade] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.cash <= 0:
            raise ValueError("cash must be positive")
        self.realized_pnl = Decimal(self.realized_pnl)

    @property
    def equity(self) -> Decimal:
        return self.cash + self.realized_pnl

    def record_trade(self, trade: Trade) -> Decimal:
        """Record one completed trade and return the resulting equity."""
        if trade.net_pnl is None:
            raise ValueError("trade net_pnl is required")
        if trade.entry_index < 0 or trade.exit_index < trade.entry_index:
            raise ValueError("trade indices must be ordered")
        self.realized_pnl += Decimal(trade.net_pnl)
        self.trades.append(trade)
        return self.equity

    def record_trades(self, trades: Iterable[Trade]) -> Decimal:
        """Record completed trades in exit-time order."""
        for trade in sorted(trades, key=lambda item: (item.exit_index, item.entry_index)):
            self.record_trade(trade)
        return self.equity

    def realized_equity_curve(self) -> list[tuple[int, Decimal]]:
        """Return candle-indexed realized equity after each recorded trade."""
        equity = self.cash
        curve: list[tuple[int, Decimal]] = []
        for trade in sorted(self.trades, key=lambda item: (item.exit_index, item.entry_index)):
            equity += trade.net_pnl
            curve.append((trade.exit_index, equity))
        return curve
