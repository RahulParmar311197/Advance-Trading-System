from fastapi import APIRouter
from pydantic import BaseModel,Field
router=APIRouter(prefix="/backtest",tags=["backtest"])
class BacktestRequest(BaseModel):
    symbol:str="NIFTY"; timeframe:str="5m"; risk_per_trade:float=Field(default=.005,gt=0,le=.05); reward_risk:float=Field(default=3,gt=0)
@router.post("/validate")
def validate_request(request:BacktestRequest): return {"accepted":True,"configuration":request.model_dump()}
