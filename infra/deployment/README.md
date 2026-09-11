# Production deployment

This deployment is provider-neutral and uses the existing PostgreSQL, Redis, FastAPI, worker, scheduler, and Next.js topology. It does not provision a cloud account or commit credentials.

## Required configuration

Create an environment file outside version control with:

```dotenv
ENVIRONMENT=production
POSTGRES_DB=ats
POSTGRES_USER=ats
POSTGRES_PASSWORD=<strong-secret>
DATABASE_URL=postgresql://ats:<url-encoded-password>@db:5432/ats
REDIS_URL=redis://redis:6379/0
QUEUE_NAME=default
CODE_VERSION=<immutable-release-or-git-sha>
NEXT_PUBLIC_API_URL=https://api.example.invalid
```

`DATABASE_URL` must use the same database credentials supplied to PostgreSQL. Do not copy production secrets into the repository.

`NEXT_PUBLIC_API_URL` must be the externally reachable API origin used by the web application; replace the example value with the real deployed origin.

## Validate before startup

The application deployment boundary is fail-closed for production configuration:

```bash
ENVIRONMENT=production \
DATABASE_URL='postgresql://user:password@db:5432/ats' \
REDIS_URL='redis://redis:6379/0' \
QUEUE_NAME=default \
CODE_VERSION="$GIT_COMMIT" \
python -c 'from packages.deployment.config import load_production_settings; load_production_settings()'
```

Missing service URLs, queue name, code version, or a non-production environment are rejected.

## Start the stack

From the repository root:

```bash
docker compose -f infra/deployment/docker-compose.production.yml --env-file .env.production up -d --build
```

The production Compose file requires database/Redis URLs and credentials instead of embedding the development credentials used by the local development stack. PostgreSQL and Redis are not published to the host. API startup waits for healthy database/Redis services; the API healthcheck then requires PostgreSQL, Redis, and queue readiness before the web service can start.

## Operational checks

```bash
docker compose -f infra/deployment/docker-compose.production.yml ps
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/health/ready
```

`/health` is a liveness check. `/health/ready` is the deployment readiness check and must report healthy PostgreSQL, Redis, and queue dependencies. Live broker mode remains disabled by default elsewhere in the system.

## Rollback

Pin `CODE_VERSION` to the previous known-good application revision, rebuild the images, and restart the stack. Keep the PostgreSQL volume intact so rollback does not destroy persisted experiments or market-data records.

This repository does not claim a cloud-provider deployment until a provider, networking model, TLS termination, secret manager, backup policy, and recovery objectives are explicitly selected and validated.