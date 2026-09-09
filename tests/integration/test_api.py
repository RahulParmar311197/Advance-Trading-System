def test_api_module_imports():
    from apps.api.app.main import app
    assert any(route.path=="/health" for route in app.routes)
