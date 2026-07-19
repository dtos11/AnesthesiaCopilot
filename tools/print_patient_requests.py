"""Print raw structured patient requests from Google Calendar.

Run from the repository root with:

    .venv/bin/python tools/print_patient_requests.py
"""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.calendar.google_calendar_client import GoogleCalendarClient  # noqa: E402
from app.patient_requests_reader import PatientRequestsReader  # noqa: E402


def main() -> None:
    reader = PatientRequestsReader(GoogleCalendarClient())
    requests = reader.read()

    print(f"Found {len(requests)} patient request(s)\n")

    for patient_request in requests:
        print(patient_request)


if __name__ == "__main__":
    main()
