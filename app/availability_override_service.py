from datetime import date
import warnings

from app.availability_overrides_reader import AvailabilityOverridesReader
from app.models.availability_override import AvailabilityOverride
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


class AvailabilityOverrideService:

    def __init__(
        self,
        availability_overrides_reader: AvailabilityOverridesReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.availability_overrides_reader = availability_overrides_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()

    def get_overrides_for_date(
        self,
        day: date,
    ) -> list[AvailabilityOverride]:
        overrides = self.availability_overrides_reader.read(
            start_date=day,
            end_date=day,
        )
        return self._resolve_overrides(overrides)

    def _resolve_overrides(
        self,
        raw_overrides: list[AvailabilityOverride],
    ) -> list[AvailabilityOverride]:
        canonical_overrides = []

        for availability_override in raw_overrides:
            identity = self.staff_identity_service.try_resolve(
                availability_override.person
            )

            if not identity.resolved:
                self._warn_unknown(availability_override.person)
                continue

            canonical_overrides.append(
                AvailabilityOverride(
                    date=availability_override.date,
                    person=identity.his_full_name,
                    instructions=availability_override.instructions,
                )
            )

        return canonical_overrides

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = (
            "Unresolved staff identity from Availability overrides: "
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
