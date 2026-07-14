from datetime import datetime, UTC

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.vacation import Vacation


VACATIONS_CALENDAR_ID = (
    "3p920b0erqatd133drcpl6mko4@group.calendar.google.com"
)


class VacationsReader:

    def __init__(self, client: GoogleCalendarClient):
        self.client = client

    def read(self):

        now = datetime.now(UTC).isoformat()

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

        vacations = []

        for event in events["items"]:

            summary = event["summary"].strip()

            replacement = None

            if " cubre " in summary:
                person, replacement = summary.split(" cubre ", 1)

            elif " pendiente reemplazo" in summary:
                person = summary.replace(" pendiente reemplazo", "")

            elif " falta reemplazo" in summary:
                person = summary.replace(" falta reemplazo", "")

            else:
                person = summary

            vacations.append(
                Vacation(
                    person=person.strip(),
                    start=event["start"]["date"],
                    end=event["end"]["date"],
                    replacement=replacement.strip() if replacement else None,
                )
            )

        return vacations


def main():

    client = GoogleCalendarClient()

    vacations = VacationsReader(client).read()

    print("\n=== Upcoming vacations ===\n")

    for vacation in vacations:
        print(vacation)


if __name__ == "__main__":
    main()