from .base import Strategy
from .liquidity_mss_fvg import LiquidityMSSFVG
_REGISTRY={"Liquidity MSS FVG":LiquidityMSSFVG}
def get_strategy(name:str)->Strategy:
    try:return _REGISTRY[name]()
    except KeyError as exc:raise ValueError(f"unknown strategy: {name}") from exc
