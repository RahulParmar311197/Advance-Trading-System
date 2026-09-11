from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg

from packages.monitoring.errors import LoggingErrorTracker

from .config import settings
from .routes.backtest import router as backtest_router
from .routes.experiments import router as experiments_router
from .routes.health import router as health_router
from .routes.market_data import router as market_router

app = FastAPI(title=settings.app_name, version="0.1.0")
error_tracker = LoggingErrorTracker()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key-ID", "X-API-Key-Secret"],
)


@app.exception_handler(psycopg.OperationalError)
async def handle_database_unavailable(request: Request, exc: psycopg.OperationalError) -> JSONResponse:
    """Expose database connectivity failures as retryable service errors."""
    error_tracker.capture(request, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "database unavailable", "error": type(exc).__name__},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Track unexpected failures without exposing internal exception details."""
    error_tracker.capture(request, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "internal server error", "error": type(exc).__name__},
    )


app.include_router(health_router)
app.include_router(market_router)
app.include_router(backtest_router)
app.include_router(experiments_router)
