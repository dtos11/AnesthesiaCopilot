import unittest
from datetime import date
from types import SimpleNamespace

from app.resident_calendar_reader import ResidentCalendarReader
from app.resident_service import ResidentService


class CalendarClient:

    def list_events(self, calendar_id, time_min=None, time_max=None):
        return [
            {
                "summary": " Martinez ",
                "start": {"date": "2026-07-30"},
                "end": {"date": "2026-07-31"},
            },
            {
                "summary": " VACACIONES   Quiroga ",
                "start": {"date": "2026-07-27"},
                "end": {"date": "2026-08-03"},
            },
            {
                "summary": "Timed Resident",
                "start": {"dateTime": "2026-07-30T08:00:00-03:00"},
                "end": {"dateTime": "2026-07-30T20:00:00-03:00"},
            },
        ]


class IdentityService:

    IDENTITIES = {
        "Martinez": "Martinez Charo",
        "Quiroga": "Quiroga Luciana Marlene",
    }

    def try_resolve(self, raw_name):
        return SimpleNamespace(
            resolved=raw_name in self.IDENTITIES,
            his_full_name=self.IDENTITIES.get(raw_name),
        )


class ResidentCalendarTests(unittest.TestCase):

    def test_reader_parses_on_call_and_vacation_events(self):
        state = ResidentCalendarReader(CalendarClient()).read(
            date(2026, 7, 30)
        )

        self.assertEqual(state.resident_on_call, ("Martinez",))
        self.assertEqual(state.resident_vacations, ("Quiroga",))

    def test_service_returns_canonical_resident_names(self):
        service = ResidentService(
            ResidentCalendarReader(CalendarClient()),
            IdentityService(),
        )

        state = service.get_state_for_date(date(2026, 7, 30))

        self.assertEqual(
            state.resident_on_call,
            ("Martinez Charo",),
        )
        self.assertEqual(
            state.resident_vacations,
            ("Quiroga Luciana Marlene",),
        )


if __name__ == "__main__":
    unittest.main()
