# Scheduler service

The scheduler is a small, separate process that turns explicit recurring schedules into Redis queue jobs. It does not execute research, market-data ingestion, or trading work itself.

Configure `SCHEDULES_JSON` as a JSON array. Each item requires `name`, `job_name`, and `interval_seconds`; `queue` defaults to `default` and `payload` defaults to `{}`.

Example for an existing real backtest worker job (configure actual organization, dates, symbol, and strategy before enabling it):

```json
[
  {
    "name": "research-backtest",
    "queue": "default",
    "job_name": "backtest.run",
    "payload": {
      "organization_id": "org-actual",
      "symbol": "NIFTY",
      "timeframe": "5m",
      "start": "2026-01-01T09:15:00+05:30",
      "end": "2026-01-02T15:30:00+05:30",
      "strategy": "Liquidity MSS FVG"
    },
    "interval_seconds": 86400
  }
]
```

The service starts with no schedules when `SCHEDULES_JSON` is unset, so deployment cannot accidentally enqueue work with fabricated or missing business inputs. A missed interval creates at most one catch-up job, avoiding a restart-induced queue storm. Redis failures leave the deadline pending for retry.
