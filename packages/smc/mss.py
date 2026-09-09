from dataclasses import dataclass
from packages.market_data.models import Candle
from .swings import Swing

@dataclass(frozen=True, slots=True)
class MSSEvent: index:int; direction:str; level:object

def detect_mss(candles:list[Candle], swings:list[Swing])->list[MSSEvent]:
    out=[]; highs=[s for s in swings if s.kind=="high"]; lows=[s for s in swings if s.kind=="low"]
    for i,c in enumerate(candles):
        h=next((s for s in reversed(highs) if s.index<i),None); l=next((s for s in reversed(lows) if s.index<i),None)
        if h and c.close>h.price: out.append(MSSEvent(i,"bullish",h.price))
        elif l and c.close<l.price: out.append(MSSEvent(i,"bearish",l.price))
    return out
