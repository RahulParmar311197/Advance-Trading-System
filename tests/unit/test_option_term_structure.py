from datetime import datetime, timezone

import pytest

from packages.options.term_structure import ImpliedVolatilityObservation, term_structure


UTC = timezone.utc


def observation(day: int, volatility: float) -> ImpliedVolatilityObservation:
    return ImpliedVolatilityObservation(
        expiry=datetime(2026, 9, day, tzinfo=UTC),
        implied_volatility=volatility,
    )


def test_term_structure_is_sorted_by_expiry_without_interpolation() -> None:
    observations = (observation(24, 0.22), observation(17, 0.18), observation(30, 0.25))

    result = term_structure(observations)

    assert [(item.expiry.day, item.implied_volatility) for item in result] == [
        (17, 0.18),
        (24, 0.22),
        (30, 0.25),
    ]


def test_empty_term_structure_fails_closed() -> None:
    with pytest.raises(ValueError, match="observations must not be empty"):
        term_structure(())


def test_duplicate_expiry_fails_closed() -> None:
    with pytest.raises(ValueError, match="duplicate expiry observation"):
        term_structure((observation(24, 0.20), observation(24, 0.22)))


def test_non_positive_iv_fails_closed() -> None:
    with pytest.raises(ValueError, match="implied_volatility must be positive"):
        observation(24, 0.0)
