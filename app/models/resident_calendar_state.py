from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ResidentCalendarState:
    date: date
    resident_on_call: tuple[str, ...]
    resident_vacations: tuple[str, ...]
