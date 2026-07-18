from datetime import date
import warnings

from app.models.saturday_roster_entry import SaturdayRosterEntry
from app.saturday_roster_reader import SaturdayRosterReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService


class SaturdayRosterService:

    def __init__(
        self,
        saturday_roster_reader: SaturdayRosterReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.saturday_roster_reader = saturday_roster_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()

    def get_entries_for_date(
        self,
        day: date,
    ) -> list[SaturdayRosterEntry]:
        entries = self.saturday_roster_reader.read(
            start_date=day,
            end_date=day,
        )
        return self._resolve_entries(entries)

    def _resolve_entries(
        self,
        raw_entries: list[SaturdayRosterEntry],
    ) -> list[SaturdayRosterEntry]:
        canonical_entries = []

        for entry in raw_entries:
            identity = self.staff_identity_service.try_resolve(
                entry.person
            )

            if not identity.resolved:
                self._warn_unknown(entry.person)
                continue

            canonical_entries.append(
                SaturdayRosterEntry(
                    date=entry.date,
                    slot=entry.slot,
                    person=identity.his_full_name,
                )
            )

        return canonical_entries

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        warnings.warn(
            f"Unresolved staff identity from Saturday roster: "
            f"'{raw_name}'",
            stacklevel=2,
        )
