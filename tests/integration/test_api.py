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
