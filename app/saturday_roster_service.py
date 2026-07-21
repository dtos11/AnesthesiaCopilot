from datetime import date
import warnings

from app.models.saturday_roster_entry import SaturdayRosterEntry
from app.saturday_roster_reader import SaturdayRosterReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


class SaturdayRosterService:

    OPERATIONAL_SLOT_LABELS = {
        "Q1": "Q1L",
        "Q2": "Q2L",
        "Q3": "Q3C",
        "Q4": "Q4L",
        "Q5": "Q5C",
        "Q6": "Q6L",
        "Q7": "Q7L",
        "E": "E",
    }
    OPERATIONAL_SLOT_ORDER = tuple(OPERATIONAL_SLOT_LABELS.values())

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
        entries = self.saturday_roster_reader.read(day)
        return self._resolve_entries(entries)

    def get_entries_for_slot(
        self,
        day: date,
        slot: str,
    ) -> list[SaturdayRosterEntry]:
        return [
            entry
            for entry in self.get_entries_for_date(day)
            if entry.slot == slot
        ]

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
                    slot=self.OPERATIONAL_SLOT_LABELS.get(
                        entry.slot,
                        entry.slot,
                    ),
                    person=identity.his_full_name,
                )
            )

        slot_order = {
            slot: index
            for index, slot in enumerate(self.OPERATIONAL_SLOT_ORDER)
        }
        canonical_entries.sort(
            key=lambda item: slot_order.get(
                item.slot,
                len(slot_order),
            )
        )
        return canonical_entries

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = (
            f"Unresolved staff identity from Saturday roster: "
            f"'{raw_name}'"
        )
        warnings.warn(
            unresolved_staff_message(
                message,
                raw_name,
                self.staff_identity_service,
            ),
            stacklevel=2,
        )
