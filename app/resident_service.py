from datetime import date
import warnings

from app.models.resident_calendar_state import ResidentCalendarState
from app.resident_calendar_reader import ResidentCalendarReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


class ResidentService:

    def __init__(
        self,
        resident_calendar_reader: ResidentCalendarReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.resident_calendar_reader = resident_calendar_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()

    def get_state_for_date(self, day: date) -> ResidentCalendarState:
        raw_state = self.resident_calendar_reader.read(day)

        return ResidentCalendarState(
            date=raw_state.date,
            resident_on_call=self._resolve_names(
                raw_state.resident_on_call
            ),
            resident_vacations=self._resolve_names(
                raw_state.resident_vacations
            ),
        )

    def _resolve_names(self, raw_names: tuple[str, ...]) -> tuple[str, ...]:
        canonical_names = []

        for raw_name in raw_names:
            identity = self.staff_identity_service.try_resolve(raw_name)

            if not identity.resolved:
                self._warn_unknown(raw_name)
                continue

            canonical_names.append(identity.his_full_name)

        return tuple(canonical_names)

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = (
            f"Unresolved staff identity from Resident calendar: "
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
