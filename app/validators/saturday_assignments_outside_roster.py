from collections import defaultdict

from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class SaturdayAssignmentsOutsideRosterValidator(Validator):

    def __init__(
        self,
        saturday_roster_service,
        staff_identity_service,
    ):
        self.saturday_roster_service = saturday_roster_service
        self.staff_identity_service = staff_identity_service

    def validate(self, cases, day):
        roster = self.saturday_roster_service.get_entries_for_date(day)
        rostered_people = {entry.person for entry in roster}
        cases_by_person = defaultdict(list)

        for case in cases:
            if case.anesthesiologist is None:
                continue

            if case.anesthesia_type == "ANESTESIA LOCAL":
                continue

            identity = self.staff_identity_service.try_resolve(
                case.anesthesiologist
            )

            if not identity.resolved:
                continue

            if identity.his_full_name not in rostered_people:
                cases_by_person[identity.his_full_name].append(case)

        return ValidationResult(
            name="Saturday assignments outside roster",
            issues=list(cases_by_person.items()),
        )
