from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AvailabilityOverride:
    date: date
    person: str
    instructions: list[str]
