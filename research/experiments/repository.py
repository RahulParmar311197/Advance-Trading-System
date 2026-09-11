from __future__ import annotations

from typing import Any

from .manifest import ExperimentManifest


class ExperimentRepository:
    """DB-API repository for organization-scoped reproducible experiments."""

    _MANIFEST_COLUMNS = """experiment_id,data_version,strategy_version,code_version,parameters,universe,
        timeframe,start_date,end_date,transaction_costs,slippage,random_seed"""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    @staticmethod
    def _require_org(organization_id: str) -> str:
        if not organization_id.strip():
            raise ValueError("organization_id must not be empty")
        return organization_id

    def save_manifest(self, manifest: ExperimentManifest, organization_id: str) -> None:
        organization_id = self._require_org(organization_id)
        r = manifest.as_record()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO experiments
                (experiment_id,organization_id,data_version,strategy_version,code_version,parameters,universe,
                 timeframe,start_date,end_date,transaction_costs,slippage,random_seed)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (experiment_id) DO NOTHING""",
                (r["experiment_id"], organization_id, r["data_version"], r["strategy_version"], r["code_version"],
                 r["parameters"], r["universe"], r["timeframe"], r["start_date"], r["end_date"],
                 r["transaction_costs"], r["slippage"], r["random_seed"]),
            )
        self.connection.commit()

    def save_results(self, experiment_id: str, organization_id: str, metrics: dict[str, Any], trades: list[dict[str, Any]]) -> None:
        organization_id = self._require_org(organization_id)
        if not experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO experiment_results (experiment_id,metrics,trades)
                SELECT %s,%s,%s WHERE EXISTS (
                    SELECT 1 FROM experiments WHERE experiment_id=%s AND organization_id=%s
                )
                ON CONFLICT (experiment_id) DO UPDATE SET metrics=EXCLUDED.metrics,trades=EXCLUDED.trades""",
                (experiment_id, metrics, trades, experiment_id, organization_id),
            )
        self.connection.commit()

    def get_manifest(self, experiment_id: str, organization_id: str) -> ExperimentManifest | None:
        organization_id = self._require_org(organization_id)
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {self._MANIFEST_COLUMNS} FROM experiments WHERE experiment_id=%s AND organization_id=%s",
                (experiment_id, organization_id),
            )
            row = cursor.fetchone()
        return self._manifest_from_row(row)

    def get_results(self, experiment_id: str, organization_id: str) -> dict[str, Any] | None:
        organization_id = self._require_org(organization_id)
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT r.metrics,r.trades FROM experiment_results r
                   JOIN experiments e ON e.experiment_id=r.experiment_id
                   WHERE r.experiment_id=%s AND e.organization_id=%s""",
                (experiment_id, organization_id),
            )
            row = cursor.fetchone()
        return None if row is None else {"metrics": row[0], "trades": row[1]}

    def list_manifests(self, organization_id: str, limit: int = 100) -> list[ExperimentManifest]:
        organization_id = self._require_org(organization_id)
        if limit < 1:
            raise ValueError("limit must be >= 1")
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {self._MANIFEST_COLUMNS} FROM experiments "
                "WHERE organization_id=%s ORDER BY created_at DESC LIMIT %s",
                (organization_id, limit),
            )
            rows = cursor.fetchall()
        return [self._manifest_from_row(row) for row in rows if row is not None]

    @staticmethod
    def _manifest_from_row(row: Any) -> ExperimentManifest | None:
        if row is None:
            return None
        return ExperimentManifest(
            experiment_id=row[0], data_version=row[1], strategy_version=row[2], code_version=row[3],
            parameters=dict(row[4]), universe=list(row[5]), timeframe=row[6], start_date=row[7],
            end_date=row[8], transaction_costs=dict(row[9]), slippage=dict(row[10]), random_seed=row[11],
        )
