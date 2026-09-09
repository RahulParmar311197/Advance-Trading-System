from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.market_data.models import Candle


@dataclass(frozen=True, slots=True)
class RegimeFeatureVector:
    """Deterministic price/volume features supplied to the regime layer."""

    period_return: Decimal
    mean_absolute_return: Decimal
    trend_slope: Decimal
    range_efficiency: Decimal
    average_volume: Decimal


def calculate_regime_features(candles: Sequence[Candle]) -> RegimeFeatureVector:
    """Calculate regime features from an ordered, non-empty candle window.

    The caller supplies the observation window and ordering. No missing market
    data, timestamps, or regime labels are inferred by this function.
    """
    if not candles:
        raise ValueError("candles must not be empty")
    ordered = tuple(candles)
    for previous, current in zip(ordered, ordered[1:]):
        if current.timestamp <= previous.timestamp:
            raise ValueError("candles must be strictly increasing by timestamp")
        if current.symbol != previous.symbol or current.timeframe != previous.timeframe:
            raise ValueError("candles must share symbol and timeframe")
    if any(candle.close <= 0 for candle in ordered):
        raise ValueError("candle close must be positive")
    if any(candle.volume < 0 for candle in ordered):
        raise ValueError("candle volume must be non-negative")

    returns = tuple(
        (current.close - previous.close) / previous.close
        for previous, current in zip(ordered, ordered[1:])
    )
    period_return = (ordered[-1].close - ordered[0].close) / ordered[0].close
    mean_absolute_return = (
        sum((abs(value) for value in returns), Decimal("0")) / Decimal(len(returns))
        if returns
        else Decimal("0")
    )
    trend_slope = _ols_slope(tuple(candle.close for candle in ordered))
    total_path = sum((abs(value) for value in returns), Decimal("0"))
    range_efficiency = (
        abs(period_return) / total_path if total_path != 0 else Decimal("0")
    )
    average_volume = sum(
        (candle.volume for candle in ordered), Decimal("0")
    ) / Decimal(len(ordered))
    return RegimeFeatureVector(
        period_return=period_return,
        mean_absolute_return=mean_absolute_return,
        trend_slope=trend_slope,
        range_efficiency=range_efficiency,
        average_volume=average_volume,
    )


def _ols_slope(values: tuple[Decimal, ...]) -> Decimal:
    if len(values) < 2:
        return Decimal("0")
    n = Decimal(len(values))
    x_mean = (n - Decimal("1")) / Decimal("2")
    y_mean = sum(values, Decimal("0")) / n
    numerator = sum(
        ((Decimal(index) - x_mean) * (value - y_mean) for index, value in enumerate(values)),
        Decimal("0"),
    )
    denominator = sum(
        ((Decimal(index) - x_mean) ** 2 for index in range(len(values))),
        Decimal("0"),
    )
    return numerator / denominator
