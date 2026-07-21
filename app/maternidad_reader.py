import re
import warnings
from datetime import date, datetime, time, timedelta, timezone

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.obstetrics_assignment import ObstetricsAssignment


MATERNIDAD_CALENDAR_ID = (
    "9jd59upgbdcml16htlm4qvuebg@group.calendar.google.com"
)

PERSON_PATTERN = r"[^\W\d_]+(?:\s+[^\W\d_]+)*"
TIME_PATTERN = r"\d{1,2}(?::\d{2})?"
SPLIT_SHIFT_PATTERN = re.compile(
    rf"^(?P<person>{PERSON_PATTERN})\s+"
    rf"{TIME_PATTERN}\s*-\s*{TIME_PATTERN}(?:\s*hs?)?$",
    re.IGNORECASE,
)
PLAIN_NAME_PATTERN = re.compile(
    rf"^{PERSON_PATTERN}$",
    re.IGNORECASE,
)


class MaternidadReader:

    def __init__(self, calendar: GoogleCalendarClient):
        self.calendar = calendar

    def read(self, day: date) -> list[ObstetricsAssignment]:
        time_min = datetime.combine(
            day,
            time.min,
            tzinfo=timezone.utc,
        )
        time_max = datetime.combine(
            day + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        events = self.calendar.list_events(
            MATERNIDAD_CALENDAR_ID,
            time_min=time_min,
            time_max=time_max,
        )

        assignments: list[ObstetricsAssignment] = []

        for event in events:
            start = event.get("start", {})
            end = event.get("end", {})
            title = (event.get("summary") or "").strip()

            if "date" not in start or "date" not in end:
                self._warn(title, "event is not all-day")
                continue

            assignment_date = date.fromisoformat(start["date"])
            end_date = date.fromisoformat(end["date"])

            if assignment_date != day:
                continue

            if (end_date - assignment_date).days != 1:
                self._warn(title, "event does not cover exactly one day")
                continue

            people = self._parse_people(title)

            if people is None:
                self._warn(title, "unsupported or malformed title")
                continue

            assignments.extend(
                ObstetricsAssignment(
                    date=assignment_date,
                    person=person,
                )
                for person in people
            )

        return assignments

    def _parse_people(self, title: str) -> list[str] | None:
        if not title:
            return None

        if title.casefold().startswith("ob-"):
            title = title[3:].strip()

        if "/" not in title:
            if PLAIN_NAME_PATTERN.fullmatch(title) is None:
                return None

            return [title]

        people = []

        for shift in title.split("/"):
            match = SPLIT_SHIFT_PATTERN.fullmatch(shift.strip())

            if match is None:
                return None

            people.append(match.group("person").strip())

        return people

    @staticmethod
    def _warn(title: str, reason: str) -> None:
        display_title = title or "<missing>"
        warnings.warn(
            f"Ignoring Maternidad event '{display_title}': {reason}",
            stacklevel=2,
        )
