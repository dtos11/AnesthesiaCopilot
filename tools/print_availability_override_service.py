"""Print canonical availability overrides for one date.

Run from the repository root with an ISO date:

    .venv/bin/python tools/print_availability_override_service.py 2026-07-20
"""

import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("schedule_date", type=date.fromisoformat)
    arguments = parser.parse_args()
    day = arguments.schedule_date
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
