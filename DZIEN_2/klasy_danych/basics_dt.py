from calendar import firstweekday
from dataclasses import dataclass,field
import time

@dataclass
class Measurement:
    value: float
    unit: str = "cm"
    timestamp: float = field(default_factory=time.time)

    # def __init__(self,value,city):
    #     self.value=value
    #     self.city=city

m =Measurement(123.7,"mm")
print(m)


