from datetime import datetime, timezone
from decimal import Decimal
import pytest
from packages.market_data.schemas import RawOHLCV
from packages.market_data.normalization import normalize_ohlcv
from packages.market_data.validation import validate_ohlcv

def test_normalize_and_validate():
    rows=[RawOHLCV(datetime(2026,1,1,9,20,tzinfo=timezone.utc),"nifty","5M",Decimal(100),Decimal(102),Decimal(99),Decimal(101),Decimal(10)),RawOHLCV(datetime(2026,1,1,9,15,tzinfo=timezone.utc),"nifty","5M",Decimal(100),Decimal(102),Decimal(99),Decimal(101),Decimal(10))]
    candles=normalize_ohlcv(rows); validate_ohlcv(candles)
    assert candles[0].timestamp.minute==15 and candles[0].symbol=="NIFTY"

def test_invalid_ohlc_rejected():
    bad=RawOHLCV(datetime(2026,1,1,9,15,tzinfo=timezone.utc),"NIFTY","5m",Decimal(100),Decimal(99),Decimal(98),Decimal(100),Decimal(10))
    with pytest.raises(ValueError): validate_ohlcv(normalize_ohlcv([bad]))
