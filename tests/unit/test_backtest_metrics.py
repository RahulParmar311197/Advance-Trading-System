from decimal import Decimal
from packages.backtest.events import Trade
from packages.backtest.metrics import build_equity_curve


def trade(entry_index: int, exit_index: int, pnl: str) -> Trade:
    return Trade(
        entry_index,
        exit_index,
        "bullish",
        Decimal("100"),
        Decimal("101"),
        Decimal("1"),
        Decimal(pnl),
        Decimal("0"),
        Decimal(pnl),
    )


def test_build_equity_curve_is_cumulative_and_aligned_to_points():
    curve = build_equity_curve(
        [trade(1, 2, "10"), trade(3, 4, "-3"), trade(3, 4, "2")],
        Decimal("100"),
        point_count=5,
    )

    assert [point["index"] for point in curve] == [0, 1, 2, 3, 4]
    assert [point["equity"] for point in curve] == [
        Decimal("100"),
        Decimal("100"),
        Decimal("110"),
        Decimal("110"),
        Decimal("109"),
    ]


def test_build_equity_curve_empty_trades_stays_at_initial_capital():
    assert build_equity_curve([], Decimal("100"), point_count=3) == [
        {"index": 0, "equity": Decimal("100")},
        {"index": 1, "equity": Decimal("100")},
        {"index": 2, "equity": Decimal("100")},
    ]
