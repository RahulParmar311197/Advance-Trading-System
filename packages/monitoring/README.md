# Monitoring

The API exposes two operational endpoints:

- `GET /health` is a liveness check and does not require backing services.
- `GET /health/ready` is a readiness check for PostgreSQL, Redis, and the configured job queue.

Readiness returns HTTP 503 when a required dependency is unavailable or Redis is not configured. Queue depth is observational only; it never substitutes for the queue's source of truth and no trading result is synthesized from a failed health check.

The queue is selected with `QUEUE_NAME` (default: `default`). Docker Compose supplies the same queue name to the API and worker.
