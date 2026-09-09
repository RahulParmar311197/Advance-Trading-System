from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from packages.regime.classifier import RegimeClassification
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class RegimeTransition:
    """One observed primary-regime change between adjacent observations."""

    from_regime: Regime
    to_regime: Regime
    observation_index: int


def detect_regime_transitions(
    classifications: Sequence[RegimeClassification],
) -> tuple[RegimeTransition, ...]:
    """Return primary-regime changes in the supplied ordered classifications.

    Ordering is supplied by the caller. No timestamps, missing observations,
    or intermediate regime labels are inferred. The returned index identifies
    the classification at which the new regime is observed.
    """
    if not classifications:
        return ()
    transitions: list[RegimeTransition] = []
    for index, (previous, current) in enumerate(
        zip(classifications, classifications[1:]), start=1
    ):
        if previous.regime != current.regime:
            transitions.append(
                RegimeTransition(
                    from_regime=previous.regime,
                    to_regime=current.regime,
                    observation_index=index,
                )
            )
    return tuple(transitions)
