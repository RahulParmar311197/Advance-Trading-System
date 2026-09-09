from decimal import Decimal
from typing import Any


def build_equity_curve(
    trades: list[Any],
    initial_capital: Decimal,
    point_count: int | None = None,
) -> list[dict[str, Decimal | int]]:
    """Build realized equity at each backtest point from closed-trade P&L.

    The current backtester has no mark-to-market position valuation, so the curve
    changes only when a trade closes. Open positions remain at the last realized
    equity until they close. When ``point_count`` is omitted, the curve ends at
    the last trade exit index.
    """
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")

    last_index = max((trade.exit_index for trade in trades), default=0)
    count = point_count if point_count is not None else last_index + 1
    if count < 1:
        return []

    pnl_by_index: dict[int, Decimal] = {}
    for trade in trades:
        if trade.exit_index < 0:
            raise ValueError("trade exit_index must be non-negative")
        pnl_by_index[trade.exit_index] = (
            pnl_by_index.get(trade.exit_index, Decimal(0)) + trade.net_pnl
        )

    equity = initial_capital
    curve: list[dict[str, Decimal | int]] = []
    for index in range(count):
        equity += pnl_by_index.get(index, Decimal(0))
        curve.append({"index": index, "equity": equity})
    return curve


def summarize(trades, initial_capital: Decimal):
    pnl = [t.net_pnl for t in trades]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x < 0]
    total = sum(pnl, Decimal(0))
    gp = sum(wins, Decimal(0))
    gl = abs(sum(losses, Decimal(0)))
    equity = initial_capital
    peak = equity
    dd = Decimal(0)
    for x in pnl:
        equity += x
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
    n = len(pnl)
    return {
        "trade_count": n,
        "total_return": total / initial_capital,
        "win_rate": Decimal(len(wins)) / Decimal(n) if n else Decimal(0),
        "profit_factor": gp / gl if gl else None,
        "expectancy": total / Decimal(n) if n else Decimal(0),
        "max_drawdown": dd / initial_capital,
        "average_trade": total / Decimal(n) if n else Decimal(0),
    }
