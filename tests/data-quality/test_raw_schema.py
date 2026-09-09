from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.market_data.schemas import RawOHLCV, validate_required_columns


def test_required_columns_reject_empty_symbol() -> None:
    row = RawOHLCV(datetime.now(timezone.utc), "", "5m", Decimal("1"), Decimal("2"), Decimal("0.5"), Decimal("1.5"), Decimal("10"))
    with pytest.raises(ValueError, match="symbol and timeframe"):
        validate_required_columns([row])
