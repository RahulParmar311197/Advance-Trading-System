from datetime import datetime, timezone

from packages.saas.auth import Role
from packages.saas.repositories import APIKeyRepository, ExperimentRepository, OrganizationRepository, UserRepository
from research.experiments.manifest import ExperimentManifest


class FakeCursor:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = rows or []
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, row=None, rows=None):
        self.cursor_instance = FakeCursor(row, rows)
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def test_organization_repository_uses_parameterized_insert_and_commit():
    connection = FakeConnection()
    record = OrganizationRepository(connection).create("org-a", "Alpha")
    assert record.organization_id == "org-a"
    assert connection.cursor_instance.executed == [
        ("INSERT INTO organizations (organization_id, name) VALUES (%s, %s)", ("org-a", "Alpha"))
    ]
    assert connection.commits == 1


def test_user_repository_round_trips_scoped_user():
    connection = FakeConnection(("user-a", "org-a", "user@example.com", "researcher", True))
    record = UserRepository(connection).get("user-a")
    assert record is not None
    assert record.organization_id == "org-a"
    assert record.role is Role.RESEARCHER
    assert record.active is True


def test_api_key_repository_never_accepts_plaintext_secret():
    digest = "a" * 64
    connection = FakeConnection()
    record = APIKeyRepository(connection).create("key-a", "org-a", "user-a", Role.TRADER, digest)
    assert record.secret_digest == digest
    query, params = connection.cursor_instance.executed[0]
    assert "secret_digest" in query
    assert params[-1] == digest
    assert "plaintext" not in str(params).lower()
    assert connection.commits == 1


def test_api_key_repository_get_and_revoke_are_parameterized():
    digest = "b" * 64
    connection = FakeConnection(("key-a", "org-a", "user-a", "trader", digest, True))
    repository = APIKeyRepository(connection)
    record = repository.get("key-a")
    repository.revoke("key-a")
    assert record is not None
    assert record.active is True
    assert connection.cursor_instance.executed[0][1] == ("key-a",)
    assert connection.cursor_instance.executed[1][1] == ("key-a",)
    assert connection.commits == 1


def test_experiment_repository_requires_and_applies_organization_scope():
    manifest = ExperimentManifest(
        experiment_id="EXP-A", data_version="DATA-A", strategy_version="s:v1", code_version="code",
        parameters={}, universe=["NIFTY"], timeframe="5m",
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 1, 2, tzinfo=timezone.utc), transaction_costs={}, slippage={},
    )
    connection = FakeConnection()
    repository = ExperimentRepository(connection)
    repository.save_manifest(manifest, "org-a")
    assert connection.cursor_instance.executed[0][1][1] == "org-a"

    scoped = FakeConnection(("EXP-A", "DATA-A", "s:v1", "code", {}, ["NIFTY"], "5m",
                             manifest.start_date, manifest.end_date, {}, {}, None))
    assert ExperimentRepository(scoped).get_manifest("EXP-A", "org-a") is not None
    assert scoped.cursor_instance.executed[0][1] == ("EXP-A", "org-a")


def test_experiment_repository_rejects_missing_organization_scope():
    try:
        ExperimentRepository(FakeConnection()).list_manifests("")
    except ValueError as exc:
        assert str(exc) == "organization_id must not be empty"
    else:
        raise AssertionError("missing organization scope must fail closed")
