from packages.saas.auth import Role
from packages.saas.repositories import APIKeyRepository, OrganizationRepository, UserRepository


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row=None):
        self.cursor_instance = FakeCursor(row)
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def test_organization_repository_uses_parameterized_insert_and_commit():
    connection = FakeConnection()
    repository = OrganizationRepository(connection)

    record = repository.create("org-a", "Alpha")

    assert record.organization_id == "org-a"
    assert connection.cursor_instance.executed == [
        ("INSERT INTO organizations (organization_id, name) VALUES (%s, %s)", ("org-a", "Alpha"))
    ]
    assert connection.commits == 1


def test_user_repository_round_trips_scoped_user():
    connection = FakeConnection(("user-a", "org-a", "user@example.com", "researcher", True))
    repository = UserRepository(connection)

    record = repository.get("user-a")

    assert record is not None
    assert record.organization_id == "org-a"
    assert record.role is Role.RESEARCHER
    assert record.active is True
    assert connection.cursor_instance.executed[0][1] == ("user-a",)


def test_api_key_repository_never_accepts_plaintext_secret():
    digest = "a" * 64
    connection = FakeConnection()
    repository = APIKeyRepository(connection)

    record = repository.create("key-a", "org-a", "user-a", Role.TRADER, digest)

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
