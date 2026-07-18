from datetime import date, datetime, time, timezone
from typing import Optional

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.call_assignment import CallAssignment


GUARDIAS_CALENDAR_ID = "7i6h1n0bmkmatdiphu1hv98n40@group.calendar.google.com"


class GuardiasReader:

    def __init__(
        self,
        calendar: GoogleCalendarClient,
        earliest_date: Optional[date] = None,
    ):
        self.calendar = calendar
        self.earliest_date = earliest_date

    def read(
        self,
        calendar_id: str = GUARDIAS_CALENDAR_ID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[CallAssignment]:

        # Preserve backward compatibility
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
            calendar_id,
            time_min=time_min,
            time_max=time_max,
        )

        assignments: list[CallAssignment] = []

        for event in events:

            summary = event.get("summary", "").strip()

            # Guardias are stored as:
            # 1-Diego Hwang
            # 2-Hernan Szmulewicz
            if "-" not in summary:
                continue

            role_text, person = summary.split("-", 1)

            role_text = role_text.strip()
            person = person.strip()

            if role_text not in ("1", "2"):
                continue

            start = event.get("start", {})

            if "date" not in start:
                continue

            assignment_date = date.fromisoformat(start["date"])

            assignments.append(
                CallAssignment(
                    date=assignment_date,
                    role=int(role_text),
                    person=person,
                )
            )

        return assignments
