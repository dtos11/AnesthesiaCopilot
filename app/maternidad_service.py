from datetime import date
import warnings

from app.maternidad_reader import MaternidadReader
from app.models.obstetrics_assignment import ObstetricsAssignment
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


class MaternidadService:

    def __init__(
        self,
        maternidad_reader: MaternidadReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.maternidad_reader = maternidad_reader
        self.staff_identity_service = staff_identity_service
        self._assignments_by_date: dict[date, list[ObstetricsAssignment]] = {}
        self._warned_unknowns = set()

    def get_assignments_for_date(
        self,
        day: date,
    ) -> list[ObstetricsAssignment]:
        if day not in self._assignments_by_date:
            assignments = []

            for assignment in self.maternidad_reader.read(day):
                identity = self.staff_identity_service.try_resolve(
                    assignment.person
                )

                if not identity.resolved:
                    self._warn_unknown(assignment.person, "Maternidad")
                    continue

                assignments.append(
                    ObstetricsAssignment(
                        date=assignment.date,
                        person=identity.his_full_name,
                    )
                )

            self._assignments_by_date[day] = assignments

        return self._assignments_by_date[day]

    def is_assigned(self, person: str, day: date) -> bool:
        identity = self.staff_identity_service.try_resolve(person)

        if not identity.resolved:
            self._warn_unknown(person, "scheduled case")
            return False

        return any(
            assignment.person == identity.his_full_name
            for assignment in self.get_assignments_for_date(day)
        )

    def _warn_unknown(self, raw_name: str, source: str) -> None:
        warning_key = (source, normalize_warning_name(raw_name))

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = f"Unresolved staff identity from {source}: '{raw_name}'"
        warnings.warn(
            unresolved_staff_message(
                message,
                raw_name,
                self.staff_identity_service,
            ),
            stacklevel=2,
        )


def normalize_warning_name(name: str) -> str:
    if not isinstance(name, str):
        return str(name)

    return " ".join(name.split()).casefold()
