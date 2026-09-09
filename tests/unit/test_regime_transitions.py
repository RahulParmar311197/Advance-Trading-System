import pytest

from packages.regime.classifier import RegimeClassification
from packages.regime.transitions import RegimeTransition, detect_regime_transitions


def classification(regime: str) -> RegimeClassification:
    return RegimeClassification(
        regime=regime,  # type: ignore[arg-type]
        trend_direction="up" if regime == "bull" else "neutral",
        volatility_state="normal",
    )


def test_transitions_returns_only_primary_regime_changes():
    observations = (
        classification("range"),
        classification("range"),
        classification("bull"),
        classification("bull"),
        classification("high_volatility"),
    )
    assert detect_regime_transitions(observations) == (
        RegimeTransition("range", "bull", 2),
        RegimeTransition("bull", "high_volatility", 4),
    )


def test_empty_observations_have_no_transitions():
    assert detect_regime_transitions(()) == ()


def test_single_observation_has_no_transition():
    assert detect_regime_transitions((classification("bull"),)) == ()


def test_identical_regimes_do_not_transition_when_secondary_labels_change():
    observations = (
        RegimeClassification("range", "neutral", "normal"),
        RegimeClassification("range", "up", "high"),
    )
    assert detect_regime_transitions(observations) == ()


def test_transition_objects_are_immutable():
    transition = RegimeTransition("bull", "bear", 1)
    with pytest.raises(AttributeError):
        transition.to_regime = "range"
