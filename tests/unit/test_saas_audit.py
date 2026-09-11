import pytest

from packages.saas.audit import build_audit_event, write_audit_event
from packages.saas.auth import Principal, Role


class Cursor:
    def __init__(self):
        self.sql = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params):
        self.sql = sql
        self.params = params


class Connection:
    def __init__(self):
        self.cursor_instance = Cursor()
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def principal():
    return Principal("user-1", "org-1", Role.TRADER)


def test_audit_event_is_scoped_to_authenticated_principal():
    event = build_audit_event(
        principal(),
        action="backtest.run",
        resource_type="experiment",
        resource_id="EXP-1",
        metadata={"strategy": "Liquidity MSS FVG"},
    )
    assert event.as_record() == {
        "organization_id": "org-1",
        "user_id": "user-1",
        "action": "backtest.run",
        "resource_type": "experiment",
        "resource_id": "EXP-1",
        "outcome": "success",
        "metadata": {"strategy": "Liquidity MSS FVG"},
    }


def test_audit_requires_authenticated_principal_and_valid_outcome():
    with pytest.raises(PermissionError, match="authenticated"):
        build_audit_event(None, action="x", resource_type="y")
    with pytest.raises(ValueError, match="invalid audit outcome"):
        build_audit_event(principal(), action="x", resource_type="y", outcome="unknown")


def test_write_audit_event_inserts_and_commits():
    connection = Connection()
    event = build_audit_event(principal(), action="order.submit", resource_type="order", resource_id="O1")
    write_audit_event(connection, event)
    assert "INSERT INTO audit_logs" in connection.cursor_instance.sql
    assert connection.cursor_instance.params[0:6] == ("org-1", "user-1", "order.submit", "order", "O1", "success")
    assert connection.commits == 1
