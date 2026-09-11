from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import os
from typing import Any
from uuid import uuid4

import psycopg

from apps.api.app.routes.backtest import BacktestRequest
from apps.api.app.routes.experiments import _json_safe, _manifest_for, _run_request
from research.experiments.repository import ExperimentRepository


def run_backtest_job(payload: dict[str, Any]) -> None:
    """Run a queued backtest and persist its reproducible experiment record."""
    required = {"organization_id", "symbol", "timeframe", "start", "end", "strategy"}
    missing = required.difference(payload)
    if missing:
        raise ValueError(f"missing job fields: {sorted(missing)}")

    request = BacktestRequest(
        symbol=payload["symbol"], timeframe=payload["timeframe"],
        start=datetime.fromisoformat(payload["start"]), end=datetime.fromisoformat(payload["end"]),
        strategy=payload["strategy"], initial_capital=Decimal(str(payload.get("initial_capital", "100000"))),
        risk_per_trade=Decimal(str(payload.get("risk_per_trade", "0.005"))),
        reward_risk=Decimal(str(payload.get("reward_risk", "3"))),
        slippage_bps=Decimal(str(payload.get("slippage_bps", "1"))), limit=int(payload.get("limit", 5000)),
    )
    with psycopg.connect(os.getenv("DATABASE_URL", "postgresql://ats:ats@localhost:5432/ats"),
                         connect_timeout=int(os.getenv("DATABASE_CONNECT_TIMEOUT_SECONDS", "5"))) as connection:
        result, data_version = _run_request(request, connection)
        experiment_id = f"EXP-{datetime.utcnow():%Y}-{uuid4().hex[:8].upper()}"
        manifest = _manifest_for(request, data_version, experiment_id)
        repository = ExperimentRepository(connection)
        repository.save_manifest(manifest, str(payload["organization_id"]))
        repository.save_results(experiment_id, str(payload["organization_id"]),
                                _json_safe(result["metrics"]), _json_safe(result["trades"]))
