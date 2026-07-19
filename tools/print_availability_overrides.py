"""Print raw availability overrides from Google Calendar.

Run from the repository root with:

    .venv/bin/python tools/print_availability_overrides.py
"""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.availability_overrides_reader import (  # noqa: E402
    AvailabilityOverridesReader,
)
from app.calendar.google_calendar_client import GoogleCalendarClient  # noqa: E402


def main() -> None:
    reader = AvailabilityOverridesReader(GoogleCalendarClient())
    overrides = reader.read()

    print(f"Found {len(overrides)} availability override(s)\n")

    for availability_override in overrides:
        print(availability_override)


if __name__ == "__main__":
    main()
