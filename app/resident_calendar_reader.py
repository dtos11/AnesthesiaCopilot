from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.resident_calendar_state import ResidentCalendarState


class ResidentCalendarReader:

    CALENDAR_ID = (
        "911071b9045f231630adff37d4c3e0804fd253a201a14791953ec5f9aa7e7d0e"
        "@group.calendar.google.com"
    )
    VACATION_PREFIX = "vacaciones"

    def __init__(self, calendar: GoogleCalendarClient):
        self.calendar = calendar

    def read(self, schedule_date: date) -> ResidentCalendarState:
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
        resident_on_call = []
        resident_vacations = []

        for event in events:
            start = event.get("start", {})
            end = event.get("end", {})

            if "date" not in start or "date" not in end:
                continue

            event_start = date.fromisoformat(start["date"])
            event_end = date.fromisoformat(end["date"])
            title = (event.get("summary") or "").strip()

            if not title:
                continue

            title_parts = title.split(maxsplit=1)

            if title_parts[0].casefold() == self.VACATION_PREFIX:
                if len(title_parts) != 2:
                    continue

                if event_start <= schedule_date < event_end:
                    resident_vacations.append(title_parts[1].strip())

                continue

            if event_start == schedule_date:
                resident_on_call.append(title)

        return ResidentCalendarState(
            date=schedule_date,
            resident_on_call=tuple(resident_on_call),
            resident_vacations=tuple(resident_vacations),
        )
