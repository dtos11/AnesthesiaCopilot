from datetime import date, datetime, time, timezone
from typing import Optional

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
        earliest_date: Optional[date] = None,
    ):
        self.calendar = calendar
        self.earliest_date = earliest_date

    def read(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[AvailabilityOverride]:
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
        overrides = []

        for event in events:
            start = event.get("start", {})

            if "date" not in start:
                continue

            override_date = date.fromisoformat(start["date"])

            if start_date is not None and override_date < start_date:
                continue

            if end_date is not None and override_date > end_date:
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
