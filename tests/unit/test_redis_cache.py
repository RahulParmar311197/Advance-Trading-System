import pytest

from packages.cache.redis_cache import CacheError, RedisCache


class FakeRedis:
    def __init__(self, value=None):
        self.value = value
        self.calls = []

    def get(self, key):
        self.calls.append(("get", key))
        return self.value

    def setex(self, key, time, value):
        self.calls.append(("setex", key, time, value))
        self.value = value
        return True

    def delete(self, key):
        self.calls.append(("delete", key))
        return 1


def test_cache_key_is_namespaced_and_deterministic():
    cache = RedisCache(FakeRedis(), namespace="ats")
    assert cache.key("smc", timeframe="5m", symbol="NIFTY") == cache.key(
        "smc", symbol="NIFTY", timeframe="5m"
    )
    assert cache.key("smc", symbol="NIFTY").startswith("ats:smc:")


def test_json_round_trip_uses_ttl():
    client = FakeRedis()
    cache = RedisCache(client)
    key = cache.key("events", symbol="NIFTY")
    cache.set_json(key, [{"event": "bullish_mss"}], ttl_seconds=60)
    assert cache.get_json(key) == [{"event": "bullish_mss"}]
    assert client.calls[0][0] == "setex"
    assert client.calls[0][2] == 60


def test_cache_rejects_invalid_ttl_and_empty_namespace():
    with pytest.raises(ValueError, match="namespace"):
        RedisCache(FakeRedis(), namespace=" ")
    with pytest.raises(ValueError, match="ttl_seconds"):
        RedisCache(FakeRedis()).set_json("key", {}, ttl_seconds=0)


def test_cache_decode_failures_are_typed():
    cache = RedisCache(FakeRedis(b"not-json"))
    with pytest.raises(CacheError, match="redis get failed"):
        cache.get_json("key")


def test_cache_delete_delegates():
    client = FakeRedis()
    RedisCache(client).delete("key")
    assert client.calls == [("delete", "key")]
