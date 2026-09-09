from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.app.config import settings
from apps.api.app.dependencies import get_connection
from apps.api.app.routes.backtest import BacktestRequest, _load_candles, _trade_record
from packages.backtest.engine import run_backtest
from packages.backtest.metrics import summarize
from packages.instruments.symbol_map import canonical_symbol
from packages.strategies.registry import get_strategy
from research.experiments.comparison import compare_results
from research.experiments.manifest import ExperimentManifest
from research.experiments.repository import ExperimentRepository
from research.reports.generator import generate_report

router = APIRouter(prefix="/experiments", tags=["experiments"])


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _run_request(request: BacktestRequest, connection: Any) -> tuple[dict[str, Any], str]:
    try:
        symbol = canonical_symbol(request.symbol)
        strategy = get_strategy(request.strategy)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if request.start > request.end:
        raise HTTPException(400, "start must be <= end")
    if hasattr(strategy, "risk_reward"):
        strategy = replace(strategy, risk_reward=request.reward_risk)

    candles, data_version = _load_candles(
        connection, symbol, request.timeframe, request.start, request.end, request.limit
    )
    signals = strategy.signals(candles)
    trades = run_backtest(
        candles,
        signals,
        capital=request.initial_capital,
        risk_per_trade=request.risk_per_trade,
        slippage_bps=request.slippage_bps,
    )
    return {
        "status": "completed",
        "data_version": data_version,
        "strategy": request.strategy,
        "symbol": symbol,
        "timeframe": request.timeframe,
        "candle_count": len(candles),
        "signal_count": len(signals),
        "trade_count": len(trades),
        "metrics": summarize(trades, request.initial_capital),
        "trades": [_trade_record(trade) for trade in trades],
    }, data_version


def _manifest_for(request: BacktestRequest, data_version: str, experiment_id: str) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id=experiment_id,
        data_version=data_version,
        strategy_version=f"{request.strategy}:v1",
        code_version=settings.code_version,
        parameters={
            "initial_capital": str(request.initial_capital),
            "risk_per_trade": str(request.risk_per_trade),
            "reward_risk": str(request.reward_risk),
            "slippage_bps": str(request.slippage_bps),
            "limit": request.limit,
        },
        universe=[canonical_symbol(request.symbol)],
        timeframe=request.timeframe,
        start_date=request.start,
        end_date=request.end,
        transaction_costs={"commission_rate": str(Decimal("0.0003"))},
        slippage={"bps": str(request.slippage_bps)},
        random_seed=None,
    )


def _comparison_rows(repository: ExperimentRepository, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for manifest in repository.list_manifests(limit):
        result = repository.get_results(manifest.experiment_id)
        if not result:
            continue
        rows.append(
            {
                "experiment_id": manifest.experiment_id,
                "strategy_version": manifest.strategy_version,
                "metrics": result.get("metrics") or {},
            }
        )
    return rows


@router.post("")
def create_experiment(
    request: BacktestRequest,
    connection: Any = Depends(get_connection),
) -> dict[str, Any]:
    result, data_version = _run_request(request, connection)
    experiment_id = f"EXP-{datetime.now(timezone.utc):%Y}-{uuid4().hex[:8].upper()}"
    manifest = _manifest_for(request, data_version, experiment_id)
    repository = ExperimentRepository(connection)
    repository.save_manifest(manifest)
    repository.save_results(
        experiment_id,
        _json_safe(result["metrics"]),
        _json_safe(result["trades"]),
    )
    return {"experiment": manifest.as_record(), "result": result}


@router.get("")
def list_experiments(
    limit: int = Query(default=100, ge=1, le=500),
    connection: Any = Depends(get_connection),
) -> list[dict[str, Any]]:
    return [manifest.as_record() for manifest in ExperimentRepository(connection).list_manifests(limit)]


@router.get("/comparison")
def compare_experiments(
    limit: int = Query(default=100, ge=1, le=500),
    connection: Any = Depends(get_connection),
) -> dict[str, Any]:
    repository = ExperimentRepository(connection)
    comparisons = compare_results(_comparison_rows(repository, limit))
    return {"results": [comparison.as_record() for comparison in comparisons]}


@router.get("/report")
def experiment_report(
    limit: int = Query(default=100, ge=1, le=500),
    connection: Any = Depends(get_connection),
) -> dict[str, str]:
    repository = ExperimentRepository(connection)
    comparisons = compare_results(_comparison_rows(repository, limit))
    try:
        report = generate_report(comparisons)
    except ValueError as exc:
        raise HTTPException(404, "no experiment results available") from exc
    return {"format": "markdown", "content": report.as_markdown()}


@router.get("/{experiment_id}")
def get_experiment(
    experiment_id: str,
    connection: Any = Depends(get_connection),
) -> dict[str, Any]:
    repository = ExperimentRepository(connection)
    manifest = repository.get_manifest(experiment_id)
    if manifest is None:
        raise HTTPException(404, "experiment not found")
    result = repository.get_results(experiment_id)
    return {"experiment": manifest.as_record(), "result": result}


@router.post("/{experiment_id}/rerun")
def rerun_experiment(
    experiment_id: str,
    connection: Any = Depends(get_connection),
) -> dict[str, Any]:
    repository = ExperimentRepository(connection)
    manifest = repository.get_manifest(experiment_id)
    if manifest is None:
        raise HTTPException(404, "experiment not found")
    parameters = manifest.parameters
    request = BacktestRequest(
        symbol=manifest.universe[0],
        timeframe=manifest.timeframe,
        start=manifest.start_date,
        end=manifest.end_date,
        strategy=manifest.strategy_version.rsplit(":v", 1)[0],
        initial_capital=Decimal(parameters["initial_capital"]),
        risk_per_trade=Decimal(parameters["risk_per_trade"]),
        reward_risk=Decimal(parameters["reward_risk"]),
        slippage_bps=Decimal(parameters["slippage_bps"]),
        limit=int(parameters["limit"]),
    )
    result, data_version = _run_request(request, connection)
    if data_version != manifest.data_version:
        raise HTTPException(409, "stored data version is no longer available for the requested range")
    repository.save_results(
        experiment_id,
        _json_safe(result["metrics"]),
        _json_safe(result["trades"]),
    )
    return {"experiment_id": experiment_id, "replayed": True, "result": result}
