from decimal import Decimal
def apply_slippage(price:Decimal,direction:str,bps:Decimal=Decimal("1"))->Decimal:
    factor=Decimal(1)+bps/Decimal(10000) if direction=="buy" else Decimal(1)-bps/Decimal(10000)
    return price*factor
