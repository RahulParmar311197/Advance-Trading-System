from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.app.auth import require_permission
from apps.api.app.dependencies import get_connection
from apps.api.app.schemas import CandleResponse
from packages.instruments.symbol_map import canonical_symbol
from packages.market_data.models import Candle
from packages.smc.bos import detect_bos
from packages.smc.events import all_smc_events
from packages.smc.fvg import detect_fvg
from packages.smc.liquidity import detect_liquidity_sweeps
from packages.smc.mss import detect_mss
from packages.smc.swings import detect_swings

router = APIRouter(
    prefix="/market-data",
    tags=["market-data"],
    dependencies=[Depends(require_permission("read"))],
)


def _load_candles(connection: Any, symbol: str, timeframe: str, start: datetime, end: datetime, limit: int) -> list[Candle]:
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
        Candle(row[0], symbol, timeframe, *(Decimal(value) for value in row[1:]))
        for row in rows
    ]


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
    return [CandleResponse.model_validate(candle) for candle in _load_candles(connection, symbol, timeframe, start, end, limit)]


@router.get("/smc-events")
def smc_events(
    symbol: str = Query(default="NIFTY"),
    timeframe: str = Query(default="5m"),
    start: datetime = Query(...),
    end: datetime = Query(...),
    limit: int = Query(default=5000, ge=1, le=50000),
    connection: Any = Depends(get_connection),
) -> list[dict[str, Any]]:
    try:
        symbol = canonical_symbol(symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if start > end:
        raise HTTPException(400, "start must be <= end")
    data = _load_candles(connection, symbol, timeframe, start, end, limit)
    swings = detect_swings(data)
    events = all_smc_events(
        data,
        bos=detect_bos(data, swings),
        mss=detect_mss(data, swings),
        liquidity=detect_liquidity_sweeps(data, swings),
        fvg=detect_fvg(data),
    )
    return [event.as_dict() for event in events]
