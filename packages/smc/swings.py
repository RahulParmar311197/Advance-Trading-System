from dataclasses import dataclass
from packages.market_data.models import Candle

@dataclass(frozen=True, slots=True)
class Swing:
    index:int; kind:str; price:object

def detect_swings(candles:list[Candle], left:int=2, right:int=2)->list[Swing]:
    if left<1 or right<1: raise ValueError("left/right must be positive")
    out=[]
    for i in range(left,len(candles)-right):
        w=candles[i-left:i+right+1]; c=candles[i]
        if c.high==max(x.high for x in w) and sum(x.high==c.high for x in w)==1: out.append(Swing(i,"high",c.high))
        if c.low==min(x.low for x in w) and sum(x.low==c.low for x in w)==1: out.append(Swing(i,"low",c.low))
    return out
