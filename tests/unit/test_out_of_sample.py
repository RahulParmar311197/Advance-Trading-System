from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.market_data.models import Candle
from packages.strategies.base import Signal, Strategy
from research.experiments.out_of_sample import run_out_of_sample


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


class FitRecordingStrategy(Strategy):
    def __init__(self):
        self.fit_lengths = []
        self.fit_end_timestamps = []

    def fit(self, candles):
        self.fit_lengths.append(len(candles))
        self.fit_end_timestamps.append(candles[-1].timestamp)
        return self

    def signals(self, candles):
        index = len(candles) - 2
        return [
            Signal(
                index=index,
                direction="bullish",
                entry=candles[index].close,
                stop=candles[index].close - Decimal("1"),
                target=candles[index].close + Decimal("2"),
            )
        ]


def make_candles(count: int) -> list[Candle]:
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


def test_oos_uses_only_the_holdout_block_for_execution():
    result = run_out_of_sample(
        make_candles(6),
        FixedSignalStrategy(),
        test_size=3,
        initial_capital=Decimal("100000"),
        slippage_bps=Decimal("0"),
    )

    assert (result.train_start, result.train_end) == (0, 3)
    assert (result.test_start, result.test_end) == (3, 6)
    assert len(result.trades) == 1
    assert result.trades[0].entry_index == 1
    assert result.trades[0].exit_index == 2
    assert result.ending_equity > result.starting_equity


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
    assert result.trades[0].entry_index == 1


def test_oos_rejects_missing_train_or_test_period():
    with pytest.raises(ValueError, match="not enough candles"):
        run_out_of_sample(make_candles(3), FixedSignalStrategy(), test_size=3)
