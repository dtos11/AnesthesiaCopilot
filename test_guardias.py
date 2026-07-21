from datetime import date

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.guardias_reader import GuardiasReader

client = GoogleCalendarClient()
reader = GuardiasReader(client)

schedule_date = date(2026, 7, 21)

assignments = reader.read(schedule_date)

print(f"Found {len(assignments)} assignments\n")

for assignment in assignments:
    print(assignment)
