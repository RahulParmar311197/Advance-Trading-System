from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.app.dependencies import get_connection
from apps.api.app.schemas import CandleResponse
from packages.instruments.symbol_map import canonical_symbol

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/validate-symbol/{symbol}")
def validate_symbol(symbol: str) -> dict[str, str]:
    try:
        return {"symbol": canonical_symbol(symbol)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/session")
def session(timestamp: datetime) -> dict[str, Any]:
    from packages.instruments.trading_calendar import is_market_session

    return {"timestamp": timestamp, "in_session": is_market_session(timestamp)}


@router.get("/candles", response_model=list[CandleResponse])
def candles(
    symbol: str = Query(default="NIFTY"),
    timeframe: str = Query(default="5m"),
    start: datetime = Query(...),
    end: datetime = Query(...),
    limit: int = Query(default=5000, ge=1, le=50000),
    connection: Any = Depends(get_connection),
) -> list[CandleResponse]:
    try:
        symbol = canonical_symbol(symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if start > end:
        raise HTTPException(400, "start must be <= end")

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM candles
               WHERE symbol=%s AND timeframe=%s AND timestamp BETWEEN %s AND %s
               ORDER BY timestamp
               LIMIT %s""",
            (symbol, timeframe, start, end, limit),
        )
        rows = cursor.fetchall()

    return [
        CandleResponse(
            timestamp=row[0],
            symbol=symbol,
            timeframe=timeframe,
            open=Decimal(row[1]),
            high=Decimal(row[2]),
            low=Decimal(row[3]),
            close=Decimal(row[4]),
            volume=Decimal(row[5]),
        )
        for row in rows
    ]
