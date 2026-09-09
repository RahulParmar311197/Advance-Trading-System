def test_api_module_imports():
    from apps.api.app.main import app

    paths = set(app.openapi()["paths"])
    assert "/health" in paths
    assert "/market-data/candles" in paths
    assert "/market-data/smc-events" in paths
    assert "/backtest/run" in paths
    assert "/experiments" in paths
    assert "/experiments/{experiment_id}" in paths
    assert "/experiments/{experiment_id}/rerun" in paths


def test_api_allows_local_dashboard_origin():
    from apps.api.app.main import app

    middleware = next(item for item in app.user_middleware if item.cls.__name__ == "CORSMiddleware")
    assert "http://localhost:3000" in middleware.kwargs["allow_origins"]
    assert "GET" in middleware.kwargs["allow_methods"]
    assert "POST" in middleware.kwargs["allow_methods"]
