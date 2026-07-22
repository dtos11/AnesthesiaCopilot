import unittest
from datetime import date
from types import SimpleNamespace

from app.models.patient_request import PatientRequest
from app.patient_request_matcher import PatientRequestMatcher
from app.patient_request_service import PatientRequestService
from app.patient_requests_reader import PatientRequestsReader


class CalendarClient:

    def list_events(self, calendar_id, time_min=None, time_max=None):
        return [
            {
                "summary": "Megadiaz | SCAZZARRIELLO",
                "description": "",
                "start": {"date": "2026-07-20"},
                "end": {"date": "2026-07-21"},
            }
        ]


class IdentityService:

    def try_resolve(self, raw_name):
        return SimpleNamespace(
            resolved=True,
            his_full_name="Mega Diaz Federico Andres",
        )


class PatientRequestOptionalSurgeonTests(unittest.TestCase):

    def test_reader_keeps_request_without_surgeon(self):
        requests = PatientRequestsReader(CalendarClient()).read(
            date(2026, 7, 20)
        )

        self.assertEqual(len(requests), 1)
        self.assertIsNone(requests[0].surgeon)

    def test_matcher_returns_no_match_without_surgeon(self):
        request = PatientRequest(
            date=date(2026, 7, 20),
            requested_anesthesiologist="Mega Diaz Federico Andres",
            patient="SCAZZARRIELLO",
            surgeon=None,
        )

        scheduled_case = SimpleNamespace(
            date=date(2026, 7, 20),
            surgeon="Rabino",
            patient="SCAZZARRIELLO",
        )

        self.assertEqual(
            PatientRequestMatcher().match([request], [scheduled_case]),
            [],
        )

    def test_service_preserves_missing_surgeon(self):
        reader = PatientRequestsReader(CalendarClient())
        service = PatientRequestService(reader, IdentityService())

        requests = service.get_requests_for_date(date(2026, 7, 20))

        self.assertEqual(
            requests[0].requested_anesthesiologist,
            "Mega Diaz Federico Andres",
        )
        self.assertIsNone(requests[0].surgeon)

    def test_matcher_behavior_is_unchanged_with_known_surgeon(self):
        request = PatientRequest(
            date=date(2026, 7, 20),
            requested_anesthesiologist="Mega Diaz Federico Andres",
            patient="SCAZZARRIELLO",
            surgeon="Rabino",
        )
        scheduled_case = SimpleNamespace(
            date=date(2026, 7, 20),
            surgeon="Rabino Juan",
            patient="SCAZZARRIELLO SILVIA",
        )

        matches = PatientRequestMatcher().match(
            [request],
            [scheduled_case],
        )

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].confidence, 100.0)


if __name__ == "__main__":
    unittest.main()
