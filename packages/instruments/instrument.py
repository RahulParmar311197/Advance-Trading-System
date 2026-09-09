from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Instrument:
    symbol: str
    exchange: str
    segment: str = "cash"
    lot_size: int = 1
    tick_size: float = 0.05
    currency: str = "INR"
