from datetime import datetime, UTC

now = datetime.now(UTC).isoformat()

from google_calendar_client import GoogleCalendarClient


VACATIONS_CALENDAR_ID = (
    "3p920b0erqatd133drcpl6mko4@group.calendar.google.com"
)


class VacationsReader:

    def __init__(self, client: GoogleCalendarClient):
        self.client = client

    def read(self):

        now = datetime.utcnow().isoformat() + "Z"

        events = (
            self.client.service.events()
            .list(
                calendarId=VACATIONS_CALENDAR_ID,
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events["items"]


def main():

    client = GoogleCalendarClient()

    vacations = VacationsReader(client).read()

    print("\n=== Upcoming vacations ===\n")

    for vacation in vacations:
        print(vacation["summary"])


if __name__ == "__main__":
    main()