from dataclasses import dataclass
from packages.market_data.models import Candle
from .swings import Swing

@dataclass(frozen=True, slots=True)
class LiquiditySweep: index:int; direction:str; level:object

def detect_liquidity_sweeps(candles:list[Candle], swings:list[Swing])->list[LiquiditySweep]:
    out=[]
    for i,c in enumerate(candles):
        h=next((s for s in reversed(swings) if s.kind=="high" and s.index<i),None)
        l=next((s for s in reversed(swings) if s.kind=="low" and s.index<i),None)
        if h and c.high>h.price and c.close<h.price: out.append(LiquiditySweep(i,"bearish",h.price))
        if l and c.low<l.price and c.close>l.price: out.append(LiquiditySweep(i,"bullish",l.price))
    return out
