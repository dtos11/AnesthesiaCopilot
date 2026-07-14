from google_calendar_client import GoogleCalendarClient


def main():
    client = GoogleCalendarClient()

    calendars = client.service.calendarList().list().execute()

    print("\n=== My Calendars ===\n")

    for calendar in calendars["items"]:
        print(calendar["summary"])


if __name__ == "__main__":
    main()