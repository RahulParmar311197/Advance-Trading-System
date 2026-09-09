from datetime import date, time, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

def is_trading_day(day: date) -> bool:
    return day.weekday() < 5

def is_market_session(timestamp: datetime) -> bool:
    local = timestamp.astimezone(IST)
    return is_trading_day(local.date()) and MARKET_OPEN <= local.time() <= MARKET_CLOSE
