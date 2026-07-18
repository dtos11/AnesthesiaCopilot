from datetime import date, datetime, time, timezone
from typing import Optional

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.saturday_roster_entry import SaturdayRosterEntry


class SaturdayRosterReader:

    CALENDAR_ID = "1a8jqctstcrolfikfv1v92sq08@group.calendar.google.com"

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
    ) -> list[SaturdayRosterEntry]:

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

            if start_date is not None and entry_date < start_date:
                continue

            if end_date is not None and entry_date > end_date:
                continue

            entries.append(
                SaturdayRosterEntry(
                    date=entry_date,
                    slot=slot,
                    person=person,
                )
            )

        return entries
