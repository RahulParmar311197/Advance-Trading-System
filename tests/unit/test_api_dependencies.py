from types import SimpleNamespace


def test_get_connection_uses_bounded_database_connect_timeout(monkeypatch):
    import apps.api.app.dependencies as dependencies

    captured = {}

    class FakeConnection:
        def close(self):
            captured["closed"] = True

    def fake_connect(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeConnection()

    monkeypatch.setattr(dependencies.psycopg, "connect", fake_connect)
    monkeypatch.setattr(
        dependencies,
        "settings",
        SimpleNamespace(database_url="postgresql://test", database_connect_timeout_seconds=7),
    )

    connection_generator = dependencies.get_connection()
    connection = next(connection_generator)
    assert connection is not None
    assert captured == {
        "url": "postgresql://test",
        "connect_timeout": 7,
    }

    connection_generator.close()
    assert captured["closed"] is True
