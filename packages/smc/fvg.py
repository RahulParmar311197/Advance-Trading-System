from dataclasses import dataclass
from packages.market_data.models import Candle

@dataclass(frozen=True, slots=True)
class FVG: index:int; direction:str; low:object; high:object

def detect_fvg(candles:list[Candle])->list[FVG]:
    out=[]
    for i in range(2,len(candles)):
        a,b,c=candles[i-2:i+1]
        if c.low>a.high: out.append(FVG(i,"bullish",a.high,c.low))
        if c.high<a.low: out.append(FVG(i,"bearish",c.high,a.low))
    return out
