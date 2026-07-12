from dataclasses import dataclass
from datetime import time


@dataclass
class Case:
    area: str
    operating_room: str
    scheduled_time: time
    duration_minutes: int | None
    patient: str
    surgeon: str
    anesthesia_type: str
    anesthesiologist: str