"""Print canonical availability overrides for one date.

Run from the repository root, optionally supplying an ISO date:

    .venv/bin/python tools/print_availability_override_service.py 2026-07-20
"""

from datetime import date
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.availability_override_service import (  # noqa: E402
    AvailabilityOverrideService,
)
from app.availability_overrides_reader import (  # noqa: E402
    AvailabilityOverridesReader,
)
from app.calendar.google_calendar_client import GoogleCalendarClient  # noqa: E402
from app.staff_directory_reader import StaffDirectoryReader  # noqa: E402
from app.staff_identity_service import StaffIdentityService  # noqa: E402


def main() -> None:
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    identity_service = StaffIdentityService(
        StaffDirectoryReader(
            REPOSITORY_ROOT / "sample_data/department_staff.xlsx"
        )
    )
    service = AvailabilityOverrideService(
        AvailabilityOverridesReader(GoogleCalendarClient()),
        identity_service,
    )
    overrides = service.get_overrides_for_date(day)

    print(f"Found {len(overrides)} availability override(s) for {day}\n")

    for availability_override in overrides:
        print(availability_override)


if __name__ == "__main__":
    main()
