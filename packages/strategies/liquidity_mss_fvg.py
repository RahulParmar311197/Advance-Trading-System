from dataclasses import dataclass
from decimal import Decimal
from packages.market_data.models import Candle
from packages.smc.swings import detect_swings
from packages.smc.liquidity import detect_liquidity_sweeps
from packages.smc.mss import detect_mss
from packages.smc.fvg import detect_fvg
from .base import Strategy, Signal

@dataclass(frozen=True, slots=True)
class LiquidityMSSFVG(Strategy):
    risk_reward:Decimal=Decimal("3")
    swing_left:int=2
    swing_right:int=2
    def signals(self,candles:list[Candle])->list[Signal]:
        swings=detect_swings(candles,self.swing_left,self.swing_right); sweeps=detect_liquidity_sweeps(candles,swings); mss=detect_mss(candles,swings); fvgs=detect_fvg(candles); out=[]
        for fvg in fvgs:
            sweep=next((s for s in sweeps if s.direction==fvg.direction and s.index<=fvg.index),None)
            structure=next((m for m in mss if m.direction==fvg.direction and sweep and sweep.index<=m.index<=fvg.index),None)
            if not sweep or not structure: continue
            c=candles[fvg.index]
            if fvg.direction=="bullish":
                stop=min(c.low,sweep.level); entry=fvg.low; target=entry+(entry-stop)*self.risk_reward
                if stop<entry: out.append(Signal(fvg.index,"bullish",entry,stop,target))
            else:
                stop=max(c.high,sweep.level); entry=fvg.high; target=entry-(stop-entry)*self.risk_reward
                if stop>entry: out.append(Signal(fvg.index,"bearish",entry,stop,target))
        return out
