from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PatientRequest:
    date: date
    requested_anesthesiologist: str
    patient: str
    surgeon: str | None
