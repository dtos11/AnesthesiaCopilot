import os
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


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
                creds.refresh(Request())

            else:
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

            response = (
                self.service.events()
                .list(**request)
                .execute()
            )

            events.extend(response.get("items", []))

            page_token = response.get("nextPageToken")

            if page_token is None:
                break

        return events