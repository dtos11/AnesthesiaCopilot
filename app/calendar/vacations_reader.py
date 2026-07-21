
from datetime import date, datetime, time, timedelta, timezone
from app.calendar.google_calendar_client import GoogleCalendarClient
from app.models.vacation import Vacation


VACATIONS_CALENDAR_ID = (
    "3p920b0erqatd133drcpl6mko4@group.calendar.google.com"
)


class VacationsReader:

    def __init__(self, client: GoogleCalendarClient):
        self.client = client

    def read(self, schedule_date: date) -> list[Vacation]:
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
        events = self.client.list_events(
            VACATIONS_CALENDAR_ID,
            time_min=time_min,
            time_max=time_max,
        )

        vacations = []

        for event in events:

            start = event.get("start", {})
            end = event.get("end", {})

            if "date" not in start or "date" not in end:
                continue

            summary = (event.get("summary") or "").strip()

            if not summary:
                continue

            vacation = Vacation(
                person=summary,
                start=date.fromisoformat(start["date"]),
                end=date.fromisoformat(end["date"]),
            )

            if vacation.includes(schedule_date):
                vacations.append(vacation)

        return vacations


def main():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("schedule_date", type=date.fromisoformat)
    arguments = parser.parse_args()

    client = GoogleCalendarClient()

    vacations = VacationsReader(client).read(arguments.schedule_date)

    print(f"\n=== Vacations on {arguments.schedule_date} ===\n")

    for vacation in vacations:
        print(vacation)


if __name__ == "__main__":
    main()
