from decimal import Decimal
from packages.market_data.models import Candle

def vwap(candles: list[Candle]) -> list[Decimal]:
    pv=Decimal(0); volume=Decimal(0); out=[]
    for c in candles:
        typical=(c.high+c.low+c.close)/Decimal(3); pv += typical*c.volume; volume += c.volume
        out.append(pv/volume if volume else typical)
    return out
