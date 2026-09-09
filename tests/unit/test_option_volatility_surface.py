from datetime import datetime, timezone

import pytest

from packages.options.volatility_surface import VolatilitySurfacePoint, volatility_surface


UTC = timezone.utc


def point(day: int, strike: float, volatility: float) -> VolatilitySurfacePoint:
    return VolatilitySurfacePoint(
        expiry=datetime(2026, 9, day, tzinfo=UTC),
        strike=strike,
        implied_volatility=volatility,
    )


def test_volatility_surface_is_sorted_by_expiry_then_strike() -> None:
    observations = (point(24, 25_200, 0.21), point(17, 25_300, 0.19), point(17, 25_100, 0.20))

    result = volatility_surface(observations)

    assert [(item.expiry.day, item.strike, item.implied_volatility) for item in result] == [
        (17, 25_100, 0.20),
        (17, 25_300, 0.19),
        (24, 25_200, 0.21),
    ]


def test_volatility_surface_does_not_infer_missing_grid_points() -> None:
    observations = (point(17, 25_100, 0.20), point(24, 25_300, 0.24))

    assert volatility_surface(observations) == observations


def test_empty_volatility_surface_fails_closed() -> None:
    with pytest.raises(ValueError, match="observations must not be empty"):
        volatility_surface(())


def test_duplicate_expiry_strike_fails_closed() -> None:
    with pytest.raises(ValueError, match="duplicate expiry/strike observation"):
        volatility_surface((point(17, 25_100, 0.20), point(17, 25_100, 0.22)))


def test_invalid_surface_point_fails_closed() -> None:
    with pytest.raises(ValueError, match="strike must be positive"):
        point(17, 0, 0.20)
    with pytest.raises(ValueError, match="implied_volatility must be positive"):
        point(17, 25_100, 0)
