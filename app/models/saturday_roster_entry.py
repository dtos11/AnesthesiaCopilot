from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SaturdayRosterEntry:
    date: date
    slot: str
    person: str
