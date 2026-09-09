from decimal import Decimal
from packages.indicators.ema import ema

def test_ema_seed():
    assert ema([Decimal(1),Decimal(2),Decimal(3)],3)[2]==Decimal(2)
