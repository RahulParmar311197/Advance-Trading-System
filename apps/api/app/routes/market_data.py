from fastapi import APIRouter,HTTPException
from datetime import datetime
from packages.instruments.symbol_map import canonical_symbol
router=APIRouter(prefix="/market-data",tags=["market-data"])
@router.get("/validate-symbol/{symbol}")
def validate_symbol(symbol:str):
    try:return {"symbol":canonical_symbol(symbol)}
    except ValueError as exc:raise HTTPException(400,str(exc)) from exc
@router.get("/session")
def session(timestamp:datetime):
    from packages.instruments.trading_calendar import is_market_session
    return {"timestamp":timestamp,"in_session":is_market_session(timestamp)}
