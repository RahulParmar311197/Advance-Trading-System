from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.out_of_sample import run_out_of_sample


def make_candles(count: int) -> list[Candle]:
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
        # Emit only on the first candle presented to the holdout evaluator.
        # This lets the test prove the evaluator translates a causal global
        # index into the local backtest index without seeing future candles.
        if len(candles) == 4:
            price = candles[-1].close
            return [
                Signal(
                    index=3,
                    direction="bullish",
                    entry=price,
                    stop=price - Decimal("1"),
                    target=price + Decimal("1"),
                )
            ]
        return []


def test_oos_fit_receives_only_training_period():
    dataset = make_candles(6)
    strategy = FitRecordingStrategy()

    result = run_out_of_sample(
        dataset,
        strategy,
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )

    assert (result.train_start, result.train_end) == (0, 3)
    assert strategy.fit_lengths == [3]
    assert strategy.fit_end_timestamps == [dataset[2].timestamp]
    assert len(result.trades) == 1
    assert result.trades[0].entry_index == 0
    assert result.trades[0].exit_index == 1


def test_oos_rejects_dataset_without_enough_train_and_test_data():
    with pytest.raises(ValueError, match="not enough candles"):
        run_out_of_sample(
            make_candles(2),
            FitRecordingStrategy(),
            test_size=2,
            initial_capital=Decimal("100000"),
            slippage_bps=Decimal("0"),
        )
