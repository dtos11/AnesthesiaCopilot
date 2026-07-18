from datetime import date
import warnings

from app.guardias_reader import GuardiasReader
from app.models.call_assignment import CallAssignment
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService


class GuardiasService:

    def __init__(
        self,
        guardias_reader: GuardiasReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.guardias_reader = guardias_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()

    def get_assignments_for_date(self, day: date) -> list[CallAssignment]:
        assignments = self.guardias_reader.read(
            start_date=day,
            end_date=day,
        )
        return self._resolve_assignments(assignments)

    def _resolve_assignments(
        self,
        raw_assignments: list[CallAssignment],
    ) -> list[CallAssignment]:
        canonical_assignments = []

        for assignment in raw_assignments:
            identity = self.staff_identity_service.try_resolve(
                assignment.person
            )

            if not identity.resolved:
                self._warn_unknown(assignment.person)
                continue

            canonical_assignments.append(
                CallAssignment(
                    date=assignment.date,
                    role=assignment.role,
                    person=identity.his_full_name,
                )
            )

        return canonical_assignments

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        warnings.warn(
            f"Unresolved staff identity from Guardias: '{raw_name}'",
            stacklevel=2,
        )
