from fastapi import FastAPI
from .config import settings
from .routes.health import router as health_router
from .routes.market_data import router as market_router
from .routes.backtest import router as backtest_router
app=FastAPI(title=settings.app_name,version="0.1.0")
app.include_router(health_router);app.include_router(market_router);app.include_router(backtest_router)
