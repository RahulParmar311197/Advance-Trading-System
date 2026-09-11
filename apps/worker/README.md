# Background worker

The worker consumes Redis-backed jobs from `QUEUE_NAME` and executes registered handlers. Claims are moved to an in-flight Redis list before execution; successful jobs are acknowledged and retryable handler failures are requeued with an incremented attempt count.

The current production job is `backtest.run`. Its payload must include `organization_id`, `symbol`, `timeframe`, `start`, `end`, and `strategy`; optional backtest parameters match the API request model. The job persists the reproducible experiment and results in PostgreSQL.

Run locally with:

```bash
REDIS_URL=redis://localhost:6379/0 DATABASE_URL=postgresql://ats:ats@localhost:5432/ats python -m apps.worker.main
```
