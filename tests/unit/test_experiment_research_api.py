from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from apps.api.app.routes.experiments import _comparison_rows, compare_experiments, experiment_report


class FakeRepository:
    def __init__(self, manifests, results):
        self._manifests = manifests
        self._results = results

    def list_manifests(self, limit):
        return self._manifests[:limit]

    def get_results(self, experiment_id):
        return self._results.get(experiment_id)


def manifest(experiment_id, strategy_version):
    return SimpleNamespace(experiment_id=experiment_id, strategy_version=strategy_version)


def result(total_return, max_drawdown):
    return {
        "metrics": {
            "trade_count": 4,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "win_rate": "0.5",
            "profit_factor": "1.5",
        }
    }


def test_comparison_rows_skip_experiments_without_results():
    repository = FakeRepository(
        [manifest("EXP-1", "S1:v1"), manifest("EXP-2", "S2:v1")],
        {"EXP-1": result("0.10", "0.05")},
    )

    assert _comparison_rows(repository, 100) == [
        {"experiment_id": "EXP-1", "strategy_version": "S1:v1", "metrics": result("0.10", "0.05")["metrics"]}
    ]


def test_comparison_endpoint_returns_json_safe_records(monkeypatch):
    repository = FakeRepository(
        [manifest("EXP-1", "S1:v1"), manifest("EXP-2", "S2:v1")],
        {"EXP-1": result("0.10", "0.05"), "EXP-2": result("0.20", "0.08")},
    )
    monkeypatch.setattr("apps.api.app.routes.experiments.ExperimentRepository", lambda _: repository)

    response = compare_experiments(100, object())

    assert response["results"][0]["experiment_id"] == "EXP-2"
    assert response["results"][0]["total_return"] == "0.20"
    assert response["results"][0]["profit_factor"] == "1.5"


def test_report_endpoint_returns_markdown(monkeypatch):
    repository = FakeRepository(
        [manifest("EXP-1", "S1:v1")],
        {"EXP-1": result("0.10", "0.05")},
    )
    monkeypatch.setattr("apps.api.app.routes.experiments.ExperimentRepository", lambda _: repository)

    response = experiment_report(100, object())

    assert response["format"] == "markdown"
    assert "# Research Comparison Report" in response["content"]
    assert "EXP-1" in response["content"]


def test_report_endpoint_returns_404_when_no_results(monkeypatch):
    repository = FakeRepository([manifest("EXP-1", "S1:v1")], {})
    monkeypatch.setattr("apps.api.app.routes.experiments.ExperimentRepository", lambda _: repository)

    with pytest.raises(Exception) as exc_info:
        experiment_report(100, object())

    assert getattr(exc_info.value, "status_code", None) == 404
