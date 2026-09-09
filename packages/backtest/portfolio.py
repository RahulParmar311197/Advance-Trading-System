from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from packages.backtest.events import Trade


def realized_equity_curve(initial_capital: Decimal, trades: Iterable[Trade]) -> list[tuple[int, Decimal]]:
    """Build a candle-indexed realized equity curve from completed trades."""
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    equity = initial_capital
    curve: list[tuple[int, Decimal]] = []
    for trade in sorted(trades, key=lambda item: (item.exit_index, item.entry_index)):
        equity += trade.net_pnl
        curve.append((trade.exit_index, equity))
    return curve


def ending_equity(initial_capital: Decimal, trades: Iterable[Trade]) -> Decimal:
    curve = realized_equity_curve(initial_capital, trades)
    return curve[-1][1] if curve else initial_capital
