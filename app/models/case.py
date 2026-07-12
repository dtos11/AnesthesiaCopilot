from dataclasses import dataclass
from datetime import time
from datetime import datetime, timedelta
from tracemalloc import start


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

    def __str__(self):

        anesthesiologist = self.anesthesiologist or "LOCAL"

        return (
            f"{self.scheduled_time.strftime('%H:%M')} | "
            f"{self.area} | "
            f"{self.operating_room} | "
            f"{self.patient} | "
            f"{anesthesiologist}"
    )

    def end_time(self):
        start = datetime.combine(datetime.today(), self.scheduled_time)
        end = start + timedelta(minutes=self.duration_minutes)
        return end.time()