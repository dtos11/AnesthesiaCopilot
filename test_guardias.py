from datetime import date, timedelta

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.guardias_reader import GuardiasReader

CALENDAR_ID = "7i6h1n0bmkmatdiphu1hv98n40@group.calendar.google.com"

client = GoogleCalendarClient()
reader = GuardiasReader(client)

today = date.today()

assignments = reader.read(
    CALENDAR_ID,
    start_date=today,
    end_date=today + timedelta(days=7),
)

print(f"Found {len(assignments)} assignments\n")

for assignment in assignments:
    print(assignment)