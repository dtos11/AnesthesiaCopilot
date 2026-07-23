import unittest
from datetime import datetime
from unittest.mock import patch

import httplib2
from googleapiclient.errors import HttpError

from app.calendar.google_calendar_client import (
    CalendarReadError,
    GoogleCalendarClient,
)


class FakeRequest:

    def __init__(self, outcome):
        self.outcome = outcome

    def execute(self):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class FakeEventsResource:

    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.list_calls = []
        self.requests = []

    def list(self, **request):
        self.list_calls.append(request)
        api_request = FakeRequest(next(self.outcomes))
        self.requests.append(api_request)
        return api_request


class FakeService:

    def __init__(self, outcomes):
        self.events_resource = FakeEventsResource(outcomes)

    def events(self):
        return self.events_resource


def calendar_client_with(outcomes):
    client = GoogleCalendarClient.__new__(GoogleCalendarClient)
    client.service = FakeService(outcomes)
    return client


class GoogleCalendarClientRetryTests(unittest.TestCase):

    def setUp(self):
        self.calendar_id = "calendar@example.com"
        self.time_min = datetime(2026, 7, 20)
        self.time_max = datetime(2026, 7, 21)

    @patch("app.calendar.google_calendar_client.time.sleep")
    def test_success_on_first_attempt(self, sleep):
        client = calendar_client_with(
            [{"items": [{"summary": "Betular"}]}]
        )

        events = client.list_events(
            self.calendar_id,
            self.time_min,
            self.time_max,
        )

        self.assertEqual(events, [{"summary": "Betular"}])
        self.assertEqual(
            len(client.service.events_resource.list_calls),
            1,
        )
        sleep.assert_not_called()

    @patch("app.calendar.google_calendar_client.time.sleep")
    def test_first_request_fails_and_second_succeeds(self, sleep):
        client = calendar_client_with(
            [
                BrokenPipeError("closed connection"),
                {"items": [{"summary": "Betular"}]},
            ]
        )

        events = client.list_events(
            self.calendar_id,
            self.time_min,
            self.time_max,
        )

        self.assertEqual(events, [{"summary": "Betular"}])
        self.assertEqual(
            len(client.service.events_resource.list_calls),
            2,
        )
        self.assertIsNot(
            client.service.events_resource.requests[0],
            client.service.events_resource.requests[1],
        )
        sleep.assert_called_once_with(1)

    @patch("app.calendar.google_calendar_client.time.sleep")
    def test_permanent_api_error_is_not_retried(self, sleep):
        forbidden = HttpError(
            httplib2.Response(
                {"status": "403", "reason": "Forbidden"}
            ),
            b'{"error": {"message": "Forbidden"}}',
        )
        client = calendar_client_with([forbidden])

        with self.assertRaises(HttpError) as raised:
            client.list_events(
                self.calendar_id,
                self.time_min,
                self.time_max,
            )

        self.assertIs(raised.exception, forbidden)
        self.assertEqual(
            len(client.service.events_resource.list_calls),
            1,
        )
        sleep.assert_not_called()

    @patch("app.calendar.google_calendar_client.time.sleep")
    def test_pagination_retries_only_the_failed_page(self, sleep):
        client = calendar_client_with(
            [
                {
                    "items": [{"summary": "First page"}],
                    "nextPageToken": "page-2",
                },
                BrokenPipeError("closed connection"),
                {"items": [{"summary": "Second page"}]},
            ]
        )

        events = client.list_events(
            self.calendar_id,
            self.time_min,
            self.time_max,
        )

        self.assertEqual(
            events,
            [
                {"summary": "First page"},
                {"summary": "Second page"},
            ],
        )
        calls = client.service.events_resource.list_calls
        self.assertNotIn("pageToken", calls[0])
        self.assertEqual(calls[1]["pageToken"], "page-2")
        self.assertEqual(calls[2]["pageToken"], "page-2")
        self.assertEqual(
            len(
                {
                    id(request)
                    for request
                    in client.service.events_resource.requests
                }
            ),
            3,
        )
        sleep.assert_called_once_with(1)

    @patch("app.calendar.google_calendar_client.time.sleep")
    def test_all_retries_fail_with_calendar_read_error(self, sleep):
        failures = [
            BrokenPipeError("failure 1"),
            BrokenPipeError("failure 2"),
            BrokenPipeError("failure 3"),
            BrokenPipeError("failure 4"),
        ]
        client = calendar_client_with(failures)

        with self.assertRaises(CalendarReadError) as raised:
            client.list_events(
                self.calendar_id,
                self.time_min,
                self.time_max,
            )

        error = raised.exception
        self.assertEqual(error.calendar_id, self.calendar_id)
        self.assertEqual(error.time_min, self.time_min)
        self.assertEqual(error.time_max, self.time_max)
        self.assertIs(error.original_exception, failures[-1])
        self.assertIsInstance(error.__cause__, BrokenPipeError)
        self.assertEqual(
            len(client.service.events_resource.list_calls),
            4,
        )
        self.assertEqual(
            [call.args for call in sleep.call_args_list],
            [(1,), (2,), (4,)],
        )


if __name__ == "__main__":
    unittest.main()
