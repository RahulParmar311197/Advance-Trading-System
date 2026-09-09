from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    symbol: str
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class CandleQuery(BaseModel):
    symbol: str = "NIFTY"
    timeframe: str = "5m"
    start: datetime
    end: datetime
    limit: int = 5000
