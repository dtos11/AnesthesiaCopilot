from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.availability_override import AvailabilityOverride


class AvailabilityOverridesReader:

    CALENDAR_ID = (
        "24fd60df2456ff487efc589bb51824c39041f492cafd2580f8b35eb8b1a1817a"
        "@group.calendar.google.com"
    )

    def __init__(
        self,
        calendar: GoogleCalendarClient,
    ):
        self.calendar = calendar

    def read(self, schedule_date: date) -> list[AvailabilityOverride]:
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
        overrides = []

        for event in events:
            start = event.get("start", {})

            if "date" not in start:
                continue

            override_date = date.fromisoformat(start["date"])

            if override_date != schedule_date:
                continue

            person = (event.get("summary") or "").strip()

            if not person:
                continue

            instructions = [
                line.strip().upper()
                for line in (event.get("description") or "").splitlines()
                if line.strip()
            ]

            overrides.append(
                AvailabilityOverride(
                    date=override_date,
                    person=person,
                    instructions=instructions,
                )
            )

        return overrides
