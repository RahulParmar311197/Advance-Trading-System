from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.app.dependencies import get_connection
from packages.backtest.engine import run_backtest
from packages.backtest.metrics import summarize
from packages.instruments.symbol_map import canonical_symbol
from packages.market_data.models import Candle
from packages.strategies.registry import get_strategy

router = APIRouter(prefix="/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "NIFTY"
    timeframe: str = "5m"
    start: datetime
    end: datetime
    strategy: str = "Liquidity MSS FVG"
    initial_capital: Decimal = Field(default=Decimal("100000"), gt=0)
    risk_per_trade: Decimal = Field(default=Decimal("0.005"), gt=0, le=Decimal("0.05"))
    reward_risk: Decimal = Field(default=Decimal("3"), gt=0)
    slippage_bps: Decimal = Field(default=Decimal("1"), ge=0)
    limit: int = Field(default=5000, ge=1, le=50000)


def _load_candles(
    connection: Any,
    symbol: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    limit: int,
) -> tuple[list[Candle], str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT timestamp, open, high, low, close, volume, data_version
               FROM candles
               WHERE symbol=%s AND timeframe=%s AND timestamp BETWEEN %s AND %s
               ORDER BY timestamp
               LIMIT %s""",
            (symbol, timeframe, start, end, limit),
        )
        rows = cursor.fetchall()

    if not rows:
        raise HTTPException(404, "no candles found for the requested range")

    versions = {row[6] for row in rows}
    if len(versions) != 1:
        raise HTTPException(409, "backtest range contains multiple data versions")

    candles = [
        Candle(row[0], symbol, timeframe, *(Decimal(value) for value in row[1:6]))
        for row in rows
    ]
    return candles, str(next(iter(versions)))


def _trade_record(trade: Any) -> dict[str, Any]:
    return {
        "entry_index": trade.entry_index,
        "exit_index": trade.exit_index,
        "direction": trade.direction,
        "entry": trade.entry,
        "exit": trade.exit,
        "quantity": trade.quantity,
        "gross_pnl": trade.gross_pnl,
        "costs": trade.costs,
        "net_pnl": trade.net_pnl,
    }


@router.post("/validate")
def validate_request(request: BacktestRequest) -> dict[str, Any]:
    if request.start > request.end:
        raise HTTPException(400, "start must be <= end")
    try:
        symbol = canonical_symbol(request.symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"accepted": True, "configuration": request.model_dump(mode="json") | {"symbol": symbol}}


@router.post("/run")
def run(
    request: BacktestRequest,
    connection: Any = Depends(get_connection),
) -> dict[str, Any]:
    if request.start > request.end:
        raise HTTPException(400, "start must be <= end")
    try:
        symbol = canonical_symbol(request.symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    try:
        strategy = get_strategy(request.strategy)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    if hasattr(strategy, "risk_reward"):
        strategy = replace(strategy, risk_reward=request.reward_risk)

    candles, data_version = _load_candles(
        connection,
        symbol,
        request.timeframe,
        request.start,
        request.end,
        request.limit,
    )
    signals = strategy.signals(candles)
    trades = run_backtest(
        candles,
        signals,
        capital=request.initial_capital,
        risk_per_trade=request.risk_per_trade,
        slippage_bps=request.slippage_bps,
    )
    metrics = summarize(trades, request.initial_capital)

    return {
        "status": "completed",
        "data_version": data_version,
        "strategy": request.strategy,
        "symbol": symbol,
        "timeframe": request.timeframe,
        "candle_count": len(candles),
        "signal_count": len(signals),
        "trade_count": len(trades),
        "metrics": metrics,
        "trades": [_trade_record(trade) for trade in trades],
    }
