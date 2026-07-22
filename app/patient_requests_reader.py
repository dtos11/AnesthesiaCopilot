from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.patient_request import PatientRequest


class PatientRequestsReader:

    CALENDAR_ID = (
        "2f30819e866424b37227b7ed01f5d90368ea255314facea42d682407e4cff0c8"
        "@group.calendar.google.com"
    )

    def __init__(
        self,
        calendar: GoogleCalendarClient,
    ):
        self.calendar = calendar

    def read(self, schedule_date: date) -> list[PatientRequest]:
        time_min = datetime.combine(
            schedule_date,
            time.min,
            tzinfo=timezone.utc,
        )
        time_max = datetime.combine(
            schedule_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        events = self.calendar.list_events(
            self.CALENDAR_ID,
            time_min=time_min,
            time_max=time_max,
        )
        requests = []

        for event in events:
            start = event.get("start", {})

            if "date" not in start:
                continue

            request_date = date.fromisoformat(start["date"])

            if request_date != schedule_date:
                continue

            title = (event.get("summary") or "").strip()

            if "|" not in title:
                continue

            requested_anesthesiologist, patient = title.split("|", 1)
            requested_anesthesiologist = requested_anesthesiologist.strip()
            patient = patient.strip()
            surgeon = self._first_non_empty_line(
                event.get("description") or ""
            ) or None

            if not requested_anesthesiologist or not patient:
                continue

            requests.append(
                PatientRequest(
                    date=request_date,
                    requested_anesthesiologist=requested_anesthesiologist,
                    patient=patient,
                    surgeon=surgeon,
                )
            )

        return requests

    @staticmethod
    def _first_non_empty_line(description: str) -> str:
        return next(
            (
                line.strip()
                for line in description.splitlines()
                if line.strip()
            ),
            "",
        )
