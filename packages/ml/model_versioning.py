from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from typing import Any

from packages.ml.datasets import FeatureDataset
from packages.ml.training import TrainingConfig


@dataclass(frozen=True, slots=True)
class ModelVersion:
    """Content-addressed identity for one fitted ML model and its provenance."""

    version_id: str
    model_name: str
    dataset_fingerprint: str
    model_fingerprint: str
    training_config: tuple[tuple[str, str], ...]


def create_model_version(
    model: object, dataset: FeatureDataset, config: TrainingConfig
) -> ModelVersion:
    """Create a deterministic model identity from fitted state and training inputs.

    The fingerprint includes the exact labeled feature matrix, explicit training
    configuration, and fitted model parameters. No timestamps or random values
    are introduced, so the same reproducible training run gets the same version.
    """
    if not is_dataclass(model):
        raise TypeError("model must be a fitted dataclass model")
    dataset_payload = {
        "features": dataset.features,
        "labels": dataset.labels,
    }
    config_payload = asdict(config)
    model_payload = asdict(model)
    dataset_fingerprint = _fingerprint(dataset_payload)
    model_fingerprint = _fingerprint(model_payload)
    config_items = tuple(
        (key, _canonical_json(value)) for key, value in sorted(config_payload.items())
    )
    version_id = _fingerprint(
        {
            "model_name": type(model).__name__,
            "dataset": dataset_fingerprint,
            "model": model_fingerprint,
            "config": config_items,
        }
    )
    return ModelVersion(
        version_id=version_id,
        model_name=type(model).__name__,
        dataset_fingerprint=dataset_fingerprint,
        model_fingerprint=model_fingerprint,
        training_config=config_items,
    )


def _fingerprint(value: Any) -> str:
    payload = _canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _canonicalize(value),
        sort_keys=True,
        separators=(",", ":"),
    )


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return {"__decimal__": str(value)}
    if isinstance(value, dict):
        return {str(key): _canonicalize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if is_dataclass(value):
        return _canonicalize(asdict(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported value for fingerprinting: {type(value).__name__}")
