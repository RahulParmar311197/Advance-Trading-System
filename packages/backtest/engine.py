from decimal import Decimal
from packages.market_data.models import Candle
from packages.strategies.base import Signal
from .commission import commission
from .events import Trade
from .slippage import apply_slippage

def run_backtest(candles:list[Candle],signals:list[Signal],capital:Decimal=Decimal("100000"),risk_per_trade:Decimal=Decimal("0.005"),slippage_bps:Decimal=Decimal("1"))->list[Trade]:
    trades=[]; equity=capital
    for signal in signals:
        if signal.index>=len(candles)-1: continue
        distance=abs(signal.entry-signal.stop)
        if distance<=0: continue
        qty=(equity*risk_per_trade/distance).quantize(Decimal("0.0001"))
        entry=apply_slippage(signal.entry,"buy" if signal.direction=="bullish" else "sell",slippage_bps)
        exit_price=exit_index=None
        for j in range(signal.index+1,len(candles)):
            c=candles[j]
            if signal.direction=="bullish":
                if c.low<=signal.stop: exit_price,exit_index=signal.stop,j; break
                if c.high>=signal.target: exit_price,exit_index=signal.target,j; break
            else:
                if c.high>=signal.stop: exit_price,exit_index=signal.stop,j; break
                if c.low<=signal.target: exit_price,exit_index=signal.target,j; break
        if exit_price is None: continue
        exit_filled=apply_slippage(exit_price,"sell" if signal.direction=="bullish" else "buy",slippage_bps)
        gross=(exit_filled-entry)*qty if signal.direction=="bullish" else (entry-exit_filled)*qty
        costs=commission(entry*qty)+commission(exit_filled*qty); net=gross-costs; equity+=net
        trades.append(Trade(signal.index,exit_index,signal.direction,entry,exit_filled,qty,gross,costs,net))
    return trades
