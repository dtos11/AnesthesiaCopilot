from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.saturday_roster_entry import SaturdayRosterEntry


class SaturdayRosterReader:

    CALENDAR_ID = "1a8jqctstcrolfikfv1v92sq08@group.calendar.google.com"

    def __init__(
        self,
        calendar: GoogleCalendarClient,
    ):
        self.calendar = calendar

    def read(self, schedule_date: date) -> list[SaturdayRosterEntry]:
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

        entries: list[SaturdayRosterEntry] = []

        for event in events:
            title = (event.get("summary") or "").strip()

            if "-" not in title:
                continue

            slot, person = title.split("-", 1)
            slot = slot.strip()
            person = person.strip()

            if not slot or not person:
                continue

            start = event.get("start", {})

            if "date" not in start:
                continue

            entry_date = date.fromisoformat(start["date"])

            if entry_date != schedule_date:
                continue

            entries.append(
                SaturdayRosterEntry(
                    date=entry_date,
                    slot=slot,
                    person=person,
                )
            )

        return entries
