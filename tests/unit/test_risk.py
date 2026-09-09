from decimal import Decimal
from packages.risk.limits import RiskLimits,check_order

def test_risk_rejects_large_order():
    ok,reason=check_order(Decimal(20000),Decimal(0),Decimal(20),RiskLimits(Decimal(10000),Decimal(5000),Decimal(100)))
    assert not ok and "position" in reason
