from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CallAssignment:
    date: date
    role: int
    person: str