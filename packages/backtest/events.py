from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True,slots=True)
class Trade:
    entry_index:int; exit_index:int; direction:str; entry:Decimal; exit:Decimal; quantity:Decimal; gross_pnl:Decimal; costs:Decimal; net_pnl:Decimal
