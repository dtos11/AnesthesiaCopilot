from dataclasses import dataclass


@dataclass(frozen=True)
class StaffRecord:
    his_full_name: str
    active: bool
    notes: str | None
    sheet: str
    row: int
