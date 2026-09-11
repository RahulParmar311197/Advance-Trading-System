from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .manifest import ExperimentManifest
from .repository import ExperimentRepository


@dataclass(frozen=True, slots=True)
class ExperimentRunResult:
    """Persisted result returned by an experiment execution."""

    manifest: ExperimentManifest
    metrics: dict[str, Any]
    trades: list[dict[str, Any]]


class ExperimentExecutor(Protocol):
    def __call__(self, manifest: ExperimentManifest) -> tuple[dict[str, Any], list[dict[str, Any]]]: ...


class ExperimentRunner:
    """Orchestrate reproducible experiment execution and persistence.

    The runner deliberately knows nothing about market data or strategy logic.
    An executor receives the complete manifest, performs the actual computation,
    and returns the computed metrics and trades. The runner persists the exact
    manifest before persisting results, so a stored result always has a
    reproducibility record associated with it.
    """

    def __init__(self, repository: ExperimentRepository) -> None:
        self.repository = repository

    def run(
        self,
        manifest: ExperimentManifest,
        organization_id: str,
        executor: ExperimentExecutor,
    ) -> ExperimentRunResult:
        self.repository.save_manifest(manifest, organization_id)
        metrics, trades = self._execute(manifest, executor)
        self.repository.save_results(manifest.experiment_id, organization_id, metrics, trades)
        return ExperimentRunResult(manifest=manifest, metrics=metrics, trades=trades)

    def rerun(
        self,
        experiment_id: str,
        organization_id: str,
        executor: ExperimentExecutor,
    ) -> ExperimentRunResult:
        manifest = self.repository.get_manifest(experiment_id, organization_id)
        if manifest is None:
            raise LookupError(f"experiment not found: {experiment_id}")
        metrics, trades = self._execute(manifest, executor)
        self.repository.save_results(experiment_id, organization_id, metrics, trades)
        return ExperimentRunResult(manifest=manifest, metrics=metrics, trades=trades)

    @staticmethod
    def _execute(
        manifest: ExperimentManifest,
        executor: ExperimentExecutor,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        metrics, trades = executor(manifest)
        if not isinstance(metrics, dict):
            raise TypeError("experiment executor must return metrics as a dict")
        if not isinstance(trades, list):
            raise TypeError("experiment executor must return trades as a list")
        return metrics, trades
