from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.walk_forward import make_windows, run_walk_forward


class FixedSignalStrategy(Strategy):
    def signals(self, candles):
        if len(candles) < 5:
            return []
        return [
            Signal(
                index=4,
                direction="bullish",
                entry=candles[4].close,
                stop=candles[4].close - Decimal("1"),
                target=candles[4].close + Decimal("2"),
            )
        ]


def candles(count: int) -> list[Candle]:
    base = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    return [
        Candle(
            base + timedelta(minutes=5 * i),
            "NIFTY",
            "5m",
            Decimal("100"),
            Decimal("102") if i == count - 1 else Decimal("100"),
            Decimal("100"),
            Decimal("100"),
            Decimal("1000"),
        )
        for i in range(count)
    ]


def test_make_windows_uses_rolling_train_then_test_blocks():
    windows = make_windows(10, train_size=4, test_size=2)
    assert [(w.train_start, w.train_end, w.test_start, w.test_end) for w in windows] == [
        (0, 4, 4, 6),
        (2, 6, 6, 8),
        (4, 8, 8, 10),
    ]


def test_walk_forward_executes_only_out_of_sample_test_blocks():
    result = run_walk_forward(
        candles(6),
        FixedSignalStrategy(),
        train_size=3,
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )

    assert len(result.windows) == 1
    assert result.windows[0]["train_start"] == 0
    assert result.windows[0]["test_start"] == 3
    assert result.windows[0]["trade_count"] == 1
    assert result.windows[0]["starting_equity"] == Decimal("100000")
    assert result.windows[0]["ending_equity"] > Decimal("100000")
    assert result.final_equity == result.windows[0]["ending_equity"]
    assert len(result.trades) == 1
    assert result.trades[0].entry_index == 1
    assert result.trades[0].exit_index == 2
