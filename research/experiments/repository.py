from __future__ import annotations

from typing import Any

from .manifest import ExperimentManifest


class ExperimentRepository:
    """DB-API repository for reproducible experiment manifests/results."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save_manifest(self, manifest: ExperimentManifest) -> None:
        r = manifest.as_record()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO experiments
                (experiment_id,data_version,strategy_version,code_version,parameters,universe,
                 timeframe,start_date,end_date,transaction_costs,slippage,random_seed)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (experiment_id) DO NOTHING""",
                (r["experiment_id"], r["data_version"], r["strategy_version"], r["code_version"],
                 r["parameters"], r["universe"], r["timeframe"], r["start_date"], r["end_date"],
                 r["transaction_costs"], r["slippage"], r["random_seed"]),
            )
        self.connection.commit()

    def save_results(self, experiment_id: str, metrics: dict[str, Any], trades: list[dict[str, Any]]) -> None:
        if not experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO experiment_results (experiment_id,metrics,trades)
                VALUES (%s,%s,%s)
                ON CONFLICT (experiment_id) DO UPDATE SET metrics=EXCLUDED.metrics,trades=EXCLUDED.trades""",
                (experiment_id, metrics, trades),
            )
        self.connection.commit()
