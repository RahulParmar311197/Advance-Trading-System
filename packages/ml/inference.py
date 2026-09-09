from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, Sequence

from packages.regime.detector import Regime


class PredictiveModel(Protocol):
    """Public fitted-model contract required by the inference boundary."""

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]: ...


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Immutable predictions returned for an explicitly supplied feature batch."""

    predictions: tuple[Regime, ...]


def run_inference(
    model: PredictiveModel, features: Sequence[Sequence[Decimal]]
) -> InferenceResult:
    """Run a fitted model without training or transforming the supplied data.

    The boundary deliberately accepts only an already-fitted model and explicit
    feature rows. It performs no data fetching, feature inference, or fallback
    prediction, so invalid model state and feature-shape errors fail closed in
    the fitted model's public prediction interface.
    """
    if not features:
        raise ValueError("features must not be empty")
    rows = tuple(tuple(row) for row in features)
    width = len(rows[0])
    if width == 0:
        raise ValueError("feature rows must not be empty")
    if any(len(row) != width for row in rows):
        raise ValueError("feature rows must have equal width")
    predictions = model.predict_many(rows)
    if len(predictions) != len(rows):
        raise ValueError("model returned an unexpected prediction count")
    return InferenceResult(predictions=predictions)
