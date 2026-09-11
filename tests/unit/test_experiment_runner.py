from datetime import datetime, timezone

import pytest

from research.experiments.manifest import ExperimentManifest
from research.experiments.runner import ExperimentRunner


class InMemoryExperimentRepository:
    def __init__(self) -> None:
        self.manifests = {}
        self.results = {}
        self.calls = []

    def save_manifest(self, manifest, organization_id):
        self.calls.append(("manifest", organization_id, manifest.experiment_id))
        self.manifests[(organization_id, manifest.experiment_id)] = manifest

    def save_results(self, experiment_id, organization_id, metrics, trades):
        self.calls.append(("results", organization_id, experiment_id))
        self.results[(organization_id, experiment_id)] = (metrics, trades)

    def get_manifest(self, experiment_id, organization_id):
        return self.manifests.get((organization_id, experiment_id))


def manifest() -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="exp-1",
        data_version="provider-v1",
        strategy_version="strategy-v1",
        code_version="code-v1",
        parameters={"risk": 0.01},
        universe=["NIFTY"],
        timeframe="5m",
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
        transaction_costs={"commission": "0.001"},
        slippage={"bps": 2},
        random_seed=7,
    )


def test_run_persists_manifest_before_results():
    repository = InMemoryExperimentRepository()
    runner = ExperimentRunner(repository)

    def executor(received):
        assert received == manifest()
        return {"net_pnl": 12}, [{"id": "trade-1"}]

    result = runner.run(manifest(), "org-1", executor)

    assert result.metrics == {"net_pnl": 12}
    assert result.trades == [{"id": "trade-1"}]
    assert repository.calls == [("manifest", "org-1", "exp-1"), ("results", "org-1", "exp-1")]


def test_rerun_uses_stored_manifest_and_replaces_results():
    repository = InMemoryExperimentRepository()
    runner = ExperimentRunner(repository)
    original = manifest()
    repository.save_manifest(original, "org-1")

    seen = []

    def executor(received):
        seen.append(received)
        return {"net_pnl": 25}, []

    result = runner.rerun("exp-1", "org-1", executor)

    assert seen == [original]
    assert result.manifest == original
    assert repository.results[("org-1", "exp-1")] == ({"net_pnl": 25}, [])


def test_rerun_fails_closed_when_experiment_is_missing():
    runner = ExperimentRunner(InMemoryExperimentRepository())

    with pytest.raises(LookupError, match="experiment not found: missing"):
        runner.rerun("missing", "org-1", lambda _: ({}, []))


def test_executor_result_shapes_are_validated():
    repository = InMemoryExperimentRepository()
    runner = ExperimentRunner(repository)

    with pytest.raises(TypeError, match="metrics as a dict"):
        runner.run(manifest(), "org-1", lambda _: ([], []))

    with pytest.raises(TypeError, match="trades as a list"):
        runner.run(manifest(), "org-1", lambda _: ({}, {}))
