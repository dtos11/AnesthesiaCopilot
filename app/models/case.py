import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass
class Case:
    area: str
    operating_room: str
    scheduled_time: time
    duration_minutes: int | None
    patient: str
    surgeon: str
    anesthesia_type: str
    anesthesiologist: str | None
    anesthesiologist_notation: str | None = None

    def __str__(self):

        anesthesiologist = self.anesthesiologist or "<unassigned>"

        return (
            f"{self.scheduled_time.strftime('%H:%M')} | "
            f"{self.area} | "
            f"{self.operating_room} | "
            f"{self.patient} | "
            f"{anesthesiologist}"
        )

    @property
    def patient_age_years(self) -> int | None:

        if not self.patient:
            return None

        match = re.search(
            r"\([^,]+,\s*(\d+)\)\s*$",
            self.patient,
        )

        if match is None:
            return None

        return int(match.group(1))

    def end_time(self):

        start = datetime.combine(
            datetime.today(),
            self.scheduled_time,
        )

        end = start + timedelta(
            minutes=self.duration_minutes
        )

        return end.time()

    def is_same_procedure(self, other):

        return (
            self.patient == other.patient
            and self.operating_room == other.operating_room
            and self.scheduled_time == other.scheduled_time
        )
