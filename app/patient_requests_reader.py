from datetime import date, datetime, time, timezone
from typing import Optional

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
        earliest_date: Optional[date] = None,
    ):
        self.calendar = calendar
        self.earliest_date = earliest_date

    def read(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[PatientRequest]:
        if start_date is None:
            start_date = self.earliest_date

        time_min = None
        if start_date is not None:
            time_min = datetime.combine(
                start_date,
                time.min,
                tzinfo=timezone.utc,
            )

        time_max = None
        if end_date is not None:
            time_max = datetime.combine(
                end_date,
                time.max,
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

            if start_date is not None and request_date < start_date:
                continue

            if end_date is not None and request_date > end_date:
                continue

            title = (event.get("summary") or "").strip()

            if "|" not in title:
                continue

            requested_anesthesiologist, patient = title.split("|", 1)
            requested_anesthesiologist = requested_anesthesiologist.strip()
            patient = patient.strip()
            surgeon = self._first_non_empty_line(
                event.get("description") or ""
            )

            if not requested_anesthesiologist or not patient or not surgeon:
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
