from dataclasses import dataclass


@dataclass(frozen=True)
class SaturdayConflict:
    slot: str
    staff: str
    final_state: str
