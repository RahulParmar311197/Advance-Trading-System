from __future__ import annotations

from decimal import Decimal
from math import sqrt
from typing import Mapping, Sequence


def pearson_correlation(left: Sequence[Decimal | int | float], right: Sequence[Decimal | int | float]) -> Decimal:
    """Calculate Pearson correlation for two equally sized return series."""
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("return series must have equal length >= 2")
    x = [float(value) for value in left]
    y = [float(value) for value in right]
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    denominator_x = sqrt(sum((a - mean_x) ** 2 for a in x))
    denominator_y = sqrt(sum((b - mean_y) ** 2 for b in y))
    if denominator_x == 0 or denominator_y == 0:
        raise ValueError("correlation is undefined for constant series")
    return Decimal(str(numerator / (denominator_x * denominator_y)))


def correlation_matrix(series: Mapping[str, Sequence[Decimal | int | float]]) -> dict[str, dict[str, Decimal]]:
    """Return a symmetric correlation matrix for named return series."""
    names = list(series)
    return {
        left: {
            right: Decimal("1") if left == right else pearson_correlation(series[left], series[right])
            for right in names
        }
        for left in names
    }
