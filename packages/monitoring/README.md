# Monitoring

The API exposes two operational endpoints:

- `GET /health` is a liveness check and does not require backing services.
- `GET /health/ready` is a readiness check for PostgreSQL, Redis, and the configured job queue.

Readiness returns HTTP 503 when a required dependency is unavailable or Redis is not configured. Queue depth is observational only; it never substitutes for the queue's source of truth and no trading result is synthesized from a failed health check.

The queue is selected with `QUEUE_NAME` (default: `default`). Docker Compose supplies the same queue name to the API and worker.

## Operational alerts

Readiness state transitions are surfaced through the application logging boundary. The first readiness observation establishes baseline state; subsequent healthy/degraded transitions emit one alert and repeated observations in the same state do not spam operators. Recovery emits a separate informational alert.

The notifier returns an explicit delivery result. A failed notification is reported as `delivery.status=failed` rather than being treated as successful delivery, while the readiness HTTP status remains determined by dependency health.

No external email, SMS, chat, or webhook credentials are required by this boundary. A future transport can implement the `AlertNotifier` protocol without changing health evaluation.
