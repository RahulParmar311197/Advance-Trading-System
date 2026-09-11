from datetime import datetime, timezone

from research.experiments.manifest import ExperimentManifest
from research.experiments.repository import ExperimentRepository


class Cursor:
    def __init__(self):
        self.calls = []
        self.fetchone_result = None
        self.fetchall_result = []

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params): self.calls.append((sql, params))
    def fetchone(self): return self.fetchone_result
    def fetchall(self): return self.fetchall_result


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


def test_repository_persists_manifest_and_results_with_scope():
    connection = Connection()
    repository = ExperimentRepository(connection)
    repository.save_manifest(manifest(), "org-a")
    repository.save_results("EXP-2026-00128", "org-a", {"win_rate": 0.5}, [{"pnl": 100}])
    assert len(connection.cursor_obj.calls) == 2
    assert connection.commits == 2
    assert "organization_id" in connection.cursor_obj.calls[0][0]
    assert connection.cursor_obj.calls[0][1][1] == "org-a"
    assert "organization_id" in connection.cursor_obj.calls[1][0]


def test_repository_reads_only_requested_organization():
    connection = Connection()
    connection.cursor_obj.fetchone_result = (
        "EXP-2026-00128", "sha256:data", "liquidity-mss-fvg:v1", "git:abc",
        {"risk_per_trade": "0.005", "rr": "3"}, ["NIFTY"], "5m",
        datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc),
        {"brokerage": "20"}, {"bps": "1"}, 42,
    )
    repository = ExperimentRepository(connection)
    loaded = repository.get_manifest("EXP-2026-00128", "org-a")
    assert loaded is not None
    assert loaded.experiment_id == manifest().experiment_id
    assert connection.cursor_obj.calls[0][1] == ("EXP-2026-00128", "org-a")

    connection.cursor_obj.fetchone_result = ({"win_rate": "0.5"}, [{"pnl": "100"}])
    results = repository.get_results("EXP-2026-00128", "org-a")
    assert results == {"metrics": {"win_rate": "0.5"}, "trades": [{"pnl": "100"}]}
    assert connection.cursor_obj.calls[1][1] == ("EXP-2026-00128", "org-a")


def test_repository_requires_scope():
    repository = ExperimentRepository(Connection())
    for operation in (
        lambda: repository.get_manifest("EXP-2026-00128", ""),
        lambda: repository.get_results("EXP-2026-00128", ""),
        lambda: repository.list_manifests(""),
    ):
        try:
            operation()
        except ValueError as exc:
            assert str(exc) == "organization_id must not be empty"
        else:
            raise AssertionError("organization scope must be mandatory")
