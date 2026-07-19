"""Print patient-request matches for a daily schedule workbook.

Run from the repository root with the Monday workbook path:

    .venv/bin/python tools/print_patient_request_matches.py \
        "/path/to/Listas del 20 de julio.xlsx"
"""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.calendar.google_calendar_client import GoogleCalendarClient  # noqa: E402
from app.case_builder import CaseBuilder  # noqa: E402
from app.patient_request_matcher import PatientRequestMatcher  # noqa: E402
from app.patient_request_service import PatientRequestService  # noqa: E402
from app.patient_requests_reader import PatientRequestsReader  # noqa: E402
from app.schedule_date_inference import infer_schedule_date  # noqa: E402
from app.staff_directory_reader import StaffDirectoryReader  # noqa: E402
from app.staff_identity_service import StaffIdentityService  # noqa: E402
from app.workbook_reader import WorkbookReader  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: .venv/bin/python tools/print_patient_request_matches.py "
            '"/path/to/schedule.xlsx"'
        )

    workbook_path = sys.argv[1]
    schedule_date = infer_schedule_date(workbook_path)
    identity_service = StaffIdentityService(
        StaffDirectoryReader(
            REPOSITORY_ROOT / "sample_data/department_staff.xlsx"
        )
    )
    workbook_reader = WorkbookReader(workbook_path)
    workbook_reader.read()
    cases = CaseBuilder(
        workbook_reader.workbook,
        schedule_date,
        identity_service,
    ).build()
    request_service = PatientRequestService(
        PatientRequestsReader(GoogleCalendarClient()),
        identity_service,
    )
    requests = request_service.get_requests_for_date(schedule_date)
    matches = PatientRequestMatcher().match(requests, cases)

    print(f"Found {len(matches)} patient request match(es)\n")

    for patient_request_match in matches:
        print(patient_request_match)


if __name__ == "__main__":
    main()
