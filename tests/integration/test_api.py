def test_api_module_imports():
    from apps.api.app.main import app

    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/health" in paths
    assert "/market-data/candles" in paths
    assert "/market-data/smc-events" in paths
