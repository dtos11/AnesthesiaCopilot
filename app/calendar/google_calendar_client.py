import logging
import os
import ssl
import time
from datetime import datetime

import httplib2
from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
RETRY_DELAYS = (1, 2, 4)
TRANSIENT_TRANSPORT_ERRORS = (
    BrokenPipeError,
    ssl.SSLError,
    ConnectionError,
    TimeoutError,
    OSError,
    TransportError,
    httplib2.ServerNotFoundError,
    httplib2.ProxiesUnavailableError,
    httplib2.FailedToDecompressContent,
)

logger = logging.getLogger(__name__)


class CalendarReadError(RuntimeError):

    def __init__(
        self,
        calendar_id: str,
        time_min: datetime | None,
        time_max: datetime | None,
        original_exception: Exception,
    ):
        self.calendar_id = calendar_id
        self.time_min = time_min
        self.time_max = time_max
        self.original_exception = original_exception
        super().__init__(
            "Unable to read Google Calendar "
            f"{calendar_id!r} for range "
            f"{time_min!s} to {time_max!s}: "
            f"{type(original_exception).__name__}: "
            f"{original_exception}"
        )


class GoogleCalendarClient:

    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):

        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES,
            )

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    print(
                        "Cached Google credentials are no longer valid."
                    )
                    print("Starting a new authentication flow...")
                    os.remove("token.json")
                    creds = None

            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES,
                )

                creds = flow.run_local_server(
                    host="localhost",
                    port=8080,
                    open_browser=True,
                )

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def _execute_with_retry(
        self,
        request_factory,
        calendar_id: str,
        time_min: datetime | None,
        time_max: datetime | None,
    ) -> dict:
        for retry_number, delay in enumerate(RETRY_DELAYS, start=1):
            try:
                return request_factory().execute()
            except TRANSIENT_TRANSPORT_ERRORS as error:
                logger.warning(
                    "Google Calendar read retry %d/%d in %d second(s): "
                    "calendar_id=%s, range=%s to %s, error=%s",
                    retry_number,
                    len(RETRY_DELAYS),
                    delay,
                    calendar_id,
                    time_min,
                    time_max,
                    type(error).__name__,
                )
                time.sleep(delay)

        try:
            return request_factory().execute()
        except TRANSIENT_TRANSPORT_ERRORS as error:
            raise CalendarReadError(
                calendar_id=calendar_id,
                time_min=time_min,
                time_max=time_max,
                original_exception=error,
            ) from error

    def list_events(
        self,
        calendar_id: str,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
    ) -> list[dict]:

        request = {
            "calendarId": calendar_id,
            "singleEvents": True,
            "orderBy": "startTime",
        }

        if time_min:
            request["timeMin"] = time_min.isoformat()

        if time_max:
            request["timeMax"] = time_max.isoformat()

        events = []
        page_token = None

        while True:

            if page_token is not None:
                request["pageToken"] = page_token
            else:
                request.pop("pageToken", None)

            response = self._execute_with_retry(
                request_factory=lambda: self.service.events().list(
                    **request
                ),
                calendar_id=calendar_id,
                time_min=time_min,
                time_max=time_max,
            )

            events.extend(response.get("items", []))

            page_token = response.get("nextPageToken")

            if page_token is None:
                break

        return events
