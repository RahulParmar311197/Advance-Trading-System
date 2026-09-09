from decimal import Decimal
def summarize(trades,initial_capital:Decimal):
    pnl=[t.net_pnl for t in trades]; wins=[x for x in pnl if x>0]; losses=[x for x in pnl if x<0]; total=sum(pnl,Decimal(0)); gp=sum(wins,Decimal(0)); gl=abs(sum(losses,Decimal(0))); equity=initial_capital; peak=equity; dd=Decimal(0)
    for x in pnl:
        equity+=x; peak=max(peak,equity); dd=max(dd,peak-equity)
    n=len(pnl)
    return {"trade_count":n,"total_return":total/initial_capital,"win_rate":Decimal(len(wins))/Decimal(n) if n else Decimal(0),"profit_factor":gp/gl if gl else None,"expectancy":total/Decimal(n) if n else Decimal(0),"max_drawdown":dd/initial_capital,"average_trade":total/Decimal(n) if n else Decimal(0)}
