from dataclasses import dataclass


@dataclass(frozen=True)
class StaffState:
    person: str
    availability: str | list[str] | None
