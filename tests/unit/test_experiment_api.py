from decimal import Decimal

from apps.api.app.routes.experiments import _json_safe


def test_json_safe_converts_decimal_values_recursively():
    value = {"metrics": {"return": Decimal("0.125")}, "trades": [{"pnl": Decimal("10.50")}]} 

    assert _json_safe(value) == {
        "metrics": {"return": "0.125"},
        "trades": [{"pnl": "10.50"}],
    }
