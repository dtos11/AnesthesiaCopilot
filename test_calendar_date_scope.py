import unittest
from datetime import date

from app.calendar.vacations_reader import VacationsReader


class RecordingCalendarClient:

    def __init__(self, events):
        self.events = events
        self.calls = []

    def list_events(self, calendar_id, time_min=None, time_max=None):
        self.calls.append((calendar_id, time_min, time_max))
        return self.events


class VacationsReaderDateScopeTests(unittest.TestCase):

    def test_reads_vacations_that_include_the_schedule_date(self):
        client = RecordingCalendarClient(
            [
                {
                    "summary": "Nozieres",
                    "start": {"date": "2026-07-18"},
                    "end": {"date": "2026-07-21"},
                },
                {
                    "summary": "Already ended",
                    "start": {"date": "2026-07-18"},
                    "end": {"date": "2026-07-20"},
                },
                {
                    "summary": "Starts later",
                    "start": {"date": "2026-07-21"},
                    "end": {"date": "2026-07-22"},
                },
            ]
        )
        schedule_date = date(2026, 7, 20)

        vacations = VacationsReader(client).read(schedule_date)

        self.assertEqual(
            [vacation.person for vacation in vacations],
            ["Nozieres"],
        )
        _, time_min, time_max = client.calls[0]
        self.assertEqual(time_min.date(), schedule_date)
        self.assertEqual(time_max.date(), date(2026, 7, 21))


if __name__ == "__main__":
    unittest.main()
