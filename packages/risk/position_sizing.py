from decimal import Decimal
def risk_quantity(equity:Decimal,risk_fraction:Decimal,entry:Decimal,stop:Decimal)->Decimal:
    distance=abs(entry-stop)
    if distance<=0: raise ValueError("entry and stop must differ")
    return equity*risk_fraction/distance
