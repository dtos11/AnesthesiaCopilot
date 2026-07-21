from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.call_assignment import CallAssignment


GUARDIAS_CALENDAR_ID = "7i6h1n0bmkmatdiphu1hv98n40@group.calendar.google.com"


class GuardiasReader:

    def __init__(
        self,
        calendar: GoogleCalendarClient,
    ):
        self.calendar = calendar

    def read(self, schedule_date: date) -> list[CallAssignment]:
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
            GUARDIAS_CALENDAR_ID,
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

            if assignment_date != schedule_date:
                continue

            assignments.append(
                CallAssignment(
                    date=assignment_date,
                    role=int(role_text),
                    person=person,
                )
            )

        return assignments
