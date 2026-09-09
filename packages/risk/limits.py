from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True,slots=True)
class RiskLimits:
    max_position_value:Decimal; max_daily_loss:Decimal; max_order_size:Decimal

def check_order(notional:Decimal,daily_loss:Decimal,quantity:Decimal,limits:RiskLimits)->tuple[bool,str]:
    if notional>limits.max_position_value:return False,"maximum position value exceeded"
    if daily_loss>=limits.max_daily_loss:return False,"maximum daily loss exceeded"
    if abs(quantity)>limits.max_order_size:return False,"maximum order size exceeded"
    return True,"accepted"
