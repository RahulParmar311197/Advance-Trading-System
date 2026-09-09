from decimal import Decimal
from packages.market_data.models import Candle

def atr(candles: list[Candle], period: int = 14) -> list[Decimal | None]:
    if period <= 0: raise ValueError("period must be positive")
    tr=[]
    for i,c in enumerate(candles):
        prev=candles[i-1].close if i else c.close
        tr.append(max(c.high-c.low,abs(c.high-prev),abs(c.low-prev)))
    out=[None]*len(tr)
    if len(tr)<period: return out
    prev=sum(tr[:period],Decimal(0))/Decimal(period); out[period-1]=prev
    for i in range(period,len(tr)):
        prev=((prev*Decimal(period-1))+tr[i])/Decimal(period); out[i]=prev
    return out
