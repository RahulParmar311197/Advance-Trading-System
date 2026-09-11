from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from apps.api.app.routes.experiments import _json_safe, rerun_experiment


def test_json_safe_converts_decimal_values_recursively():
    value = {"metrics": {"return": Decimal("0.125")}, "trades": [{"pnl": Decimal("10.50")}]}

    assert _json_safe(value) == {
        "metrics": {"return": "0.125"},
        "trades": [{"pnl": "10.50"}],
    }


def test_rerun_endpoint_delegates_execution_to_experiment_runner(monkeypatch):
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    end = datetime(2026, 1, 2, 15, 30, tzinfo=timezone.utc)
    manifest = SimpleNamespace(
        experiment_id="EXP-2026-TEST",
        data_version="data-v1",
        strategy_version="Liquidity MSS FVG:v1",
        timeframe="5m",
        start_date=start,
        end_date=end,
        universe=["NIFTY"],
        parameters={
            "initial_capital": "100000",
            "risk_per_trade": "0.005",
            "reward_risk": "3",
            "slippage_bps": "1",
            "limit": 5000,
        },
    )

    class FakeRepository:
        def __init__(self, connection):
            self.connection = connection

        def get_manifest(self, experiment_id, organization_id):
            assert experiment_id == "EXP-2026-TEST"
            assert organization_id == "org-a"
            return manifest

        def save_results(self, experiment_id, organization_id, metrics, trades):
            raise AssertionError("runner should own result persistence")

    class RunnerSpy:
        called = False

        def __init__(self, repository):
            assert isinstance(repository, FakeRepository)

        def rerun(self, experiment_id, organization_id, executor):
            assert experiment_id == "EXP-2026-TEST"
            assert organization_id == "org-a"
            RunnerSpy.called = True
            metrics, trades = executor(manifest)
            return SimpleNamespace(metrics=metrics, trades=trades)

    expected = {
        "status": "completed",
        "data_version": "data-v1",
        "strategy": "Liquidity MSS FVG",
        "symbol": "NIFTY",
        "timeframe": "5m",
        "candle_count": 3,
        "signal_count": 1,
        "trade_count": 1,
        "metrics": {"total_return": Decimal("0.1")},
        "trades": [{"pnl": Decimal("10")}],
    }

    monkeypatch.setattr("apps.api.app.routes.experiments.ExperimentRepository", FakeRepository)
    monkeypatch.setattr("apps.api.app.routes.experiments.ExperimentRunner", RunnerSpy)
    monkeypatch.setattr("apps.api.app.routes.experiments._run_request", lambda request, connection: (expected, "data-v1"))

    result = rerun_experiment("EXP-2026-TEST", SimpleNamespace(organization_id="org-a"), object())

    assert RunnerSpy.called is True
    assert result == {
        "experiment_id": "EXP-2026-TEST",
        "replayed": True,
        "result": {
            **expected,
            "metrics": {"total_return": "0.1"},
            "trades": [{"pnl": "10"}],
        },
    }
