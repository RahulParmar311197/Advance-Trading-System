from decimal import Decimal

import pytest

from packages.ml.datasets import FeatureDataset
from packages.ml.model_versioning import ModelVersion, create_model_version
from packages.ml.models import LogisticRegressionClassifier
from packages.ml.training import TrainingConfig, train_classifier


def dataset() -> FeatureDataset:
    return FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("10"),)),
        labels=("bull", "bull", "bear", "bear"),
    )


def config() -> TrainingConfig:
    return TrainingConfig(
        model="logistic", learning_rate=Decimal("0.2"), epochs=20, l2=Decimal("0.01")
    )


def test_model_version_is_deterministic_and_contains_provenance():
    first_model = train_classifier(dataset(), config())
    second_model = train_classifier(dataset(), config())
    first = create_model_version(first_model, dataset(), config())
    second = create_model_version(second_model, dataset(), config())

    assert first == second
    assert isinstance(first, ModelVersion)
    assert first.model_name == "LogisticRegressionClassifier"
    assert len(first.version_id) == 64
    assert len(first.dataset_fingerprint) == 64
    assert len(first.model_fingerprint) == 64


def test_model_version_changes_when_training_data_changes():
    model = train_classifier(dataset(), config())
    changed = FeatureDataset(
        features=((Decimal("1"),), (Decimal("2"),), (Decimal("9"),), (Decimal("11"),)),
        labels=dataset().labels,
    )
    changed_model = train_classifier(changed, config())

    original_version = create_model_version(model, dataset(), config())
    changed_version = create_model_version(changed_model, changed, config())

    assert original_version.dataset_fingerprint != changed_version.dataset_fingerprint
    assert original_version.version_id != changed_version.version_id


def test_model_version_rejects_non_dataclass_model():
    with pytest.raises(TypeError, match="dataclass"):
        create_model_version(object(), dataset(), config())


def test_model_version_preserves_explicit_training_configuration():
    model = LogisticRegressionClassifier.fit(dataset(), learning_rate=Decimal("0.2"), epochs=20, l2=Decimal("0.01"))
    version = create_model_version(model, dataset(), config())
    assert dict(version.training_config)["learning_rate"] == '"0.2"'
    assert dict(version.training_config)["epochs"] == "20"
    assert dict(version.training_config)["l2"] == '"0.01"'
