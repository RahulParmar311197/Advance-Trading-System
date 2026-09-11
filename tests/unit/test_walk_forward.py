from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.walk_forward import run_walk_forward


def candles(count: int) -> list[Candle]:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            symbol="NIFTY",
            timeframe="5m",
            open=Decimal(100 + index),
            high=Decimal(101 + index),
            low=Decimal(99 + index),
            close=Decimal(100 + index),
            volume=Decimal(1000),
        )
        for index in range(count)
    ]


class FitRecordingStrategy(Strategy):
    def __init__(self) -> None:
        self.fit_lengths: list[int] = []
        self.fit_end_timestamps: list[datetime] = []

    def fit(self, candles: list[Candle]) -> Strategy:
        self.fit_lengths.append(len(candles))
        self.fit_end_timestamps.append(candles[-1].timestamp)
        return self

    def signals(self, candles: list[Candle]) -> list[Signal]:
        # Emit only when exactly one test candle has been appended to the
        # training context. The evaluator must not expose later test candles.
        if len(candles) in (5, 4):
            price = candles[-1].close
            return [
                Signal(
                    index=len(candles) - 1,
                    direction="bullish",
                    entry=price,
                    stop=price - Decimal("1"),
                    target=price + Decimal("1"),
                )
            ]
        return []


def test_walk_forward_fit_receives_only_each_window_train_block():
    dataset = candles(10)
    strategy = FitRecordingStrategy()

    result = run_walk_forward(
        dataset,
        strategy,
        train_size=4,
        test_size=2,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )

    assert len(result.windows) == 3
    assert strategy.fit_lengths == [4, 4, 4]
    assert strategy.fit_end_timestamps == [dataset[3].timestamp, dataset[5].timestamp, dataset[7].timestamp]
    assert all(window["trade_count"] == 1 for window in result.windows)


def test_walk_forward_executes_only_out_of_sample_test_blocks():
    dataset = candles(6)
    strategy = FitRecordingStrategy()

    result = run_walk_forward(
        dataset,
        strategy,
        train_size=3,
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )

    assert len(result.windows) == 1
    assert result.windows[0]["test_start"] == 3
    assert result.windows[0]["test_end"] == 6
    assert result.windows[0]["trade_count"] == 1
