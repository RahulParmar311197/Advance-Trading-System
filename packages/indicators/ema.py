from decimal import Decimal

def ema(values: list[Decimal], period: int) -> list[Decimal | None]:
    if period <= 0: raise ValueError("period must be positive")
    out=[None]*len(values)
    if len(values)<period: return out
    previous=sum(values[:period],Decimal(0))/Decimal(period); out[period-1]=previous
    alpha=Decimal(2)/Decimal(period+1)
    for i in range(period,len(values)):
        previous=(values[i]-previous)*alpha+previous; out[i]=previous
    return out
