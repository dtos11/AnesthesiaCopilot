from dataclasses import dataclass


@dataclass(frozen=True)
class StaffAliasRecord:
    his_full_name: str
    alias: str
    source: str | None
    active: bool
    notes: str | None
    sheet: str
    row: int
