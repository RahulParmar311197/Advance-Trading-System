from abc import ABC, abstractmethod
from dataclasses import dataclass
from packages.market_data.models import Candle

@dataclass(frozen=True, slots=True)
class Signal:
    index:int; direction:str; entry:object; stop:object; target:object

class Strategy(ABC):
    @abstractmethod
    def signals(self,candles:list[Candle])->list[Signal]: ...
