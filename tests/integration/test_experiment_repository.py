from datetime import datetime, timezone

from research.experiments.manifest import ExperimentManifest
from research.experiments.repository import ExperimentRepository


class Cursor:
    def __init__(self):
        self.calls = []
        self.rowcount = 1

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params): self.calls.append((sql, params))


class Connection:
    def __init__(self): self.cursor_obj = Cursor(); self.commits = 0
    def cursor(self): return self.cursor_obj
    def commit(self): self.commits += 1


def manifest():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ExperimentManifest(
        experiment_id="EXP-2026-00128", data_version="sha256:data", strategy_version="liquidity-mss-fvg:v1",
        code_version="git:abc", parameters={"risk_per_trade": 0.005, "rr": 3}, universe=["NIFTY"],
        timeframe="5m", start_date=start, end_date=start, transaction_costs={"brokerage": 20},
        slippage={"bps": 1}, random_seed=42,
    )


def test_manifest_captures_reproducibility_fields():
    record = manifest().as_record()
    assert record["data_version"].startswith("sha256:")
    assert record["strategy_version"]
    assert record["code_version"]
    assert record["parameters"]["rr"] == 3
    assert record["random_seed"] == 42


def test_repository_persists_manifest_and_results():
    connection = Connection()
    repository = ExperimentRepository(connection)
    repository.save_manifest(manifest())
    repository.save_results("EXP-2026-00128", {"win_rate": 0.5}, [{"pnl": 100}])
    assert len(connection.cursor_obj.calls) == 2
    assert connection.commits == 2
    assert "INSERT INTO experiments" in connection.cursor_obj.calls[0][0]
    assert "INSERT INTO experiment_results" in connection.cursor_obj.calls[1][0]
