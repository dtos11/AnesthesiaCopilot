"""Print canonical patient requests returned by PatientRequestService.

Run from the repository root with an ISO date:

    .venv/bin/python tools/print_patient_request_service.py 2026-07-20
"""

import argparse
from datetime import date
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.calendar.google_calendar_client import GoogleCalendarClient  # noqa: E402
from app.patient_request_service import PatientRequestService  # noqa: E402
from app.patient_requests_reader import PatientRequestsReader  # noqa: E402
from app.staff_directory_reader import StaffDirectoryReader  # noqa: E402
from app.staff_identity_service import StaffIdentityService  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schedule_date", type=date.fromisoformat)
    arguments = parser.parse_args()
    day = arguments.schedule_date
    identity_service = StaffIdentityService(
        StaffDirectoryReader(
            REPOSITORY_ROOT / "sample_data/department_staff.xlsx"
        )
    )
    service = PatientRequestService(
        PatientRequestsReader(GoogleCalendarClient()),
        identity_service,
    )
    requests = service.get_requests_for_date(day)

    print(f"Found {len(requests)} patient request(s) for {day}\n")

    for patient_request in requests:
        print(patient_request)


if __name__ == "__main__":
    main()
