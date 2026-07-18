from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ObstetricsAssignment:
    date: date
    person: str
