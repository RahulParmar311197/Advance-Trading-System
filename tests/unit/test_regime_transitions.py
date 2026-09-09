from decimal import Decimal

from packages.regime.classifier import RegimeClassification
from packages.regime.transitions import detect_regime_transitions


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
        (lambda: None)()
    )
