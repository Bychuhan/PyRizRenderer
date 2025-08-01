from dataclasses import dataclass

@dataclass
class Judge:
    hit: int
    combo: int
    score: float
    wcd: float

judges = Judge(0, 0, 0, 0)
