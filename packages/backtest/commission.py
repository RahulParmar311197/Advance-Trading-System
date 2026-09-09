from decimal import Decimal

def commission(notional:Decimal,rate:Decimal=Decimal("0.0003"))->Decimal:return abs(notional)*rate
