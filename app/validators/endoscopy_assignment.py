from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class EndoscopyAssignmentValidator(Validator):

    def __init__(
        self,
        saturday_roster_service,
        staff_identity_service,
    ):
        self.saturday_roster_service = saturday_roster_service
        self.staff_identity_service = staff_identity_service

    def validate(self, cases, day):
        endoscopy_entries = (
            self.saturday_roster_service.get_entries_for_slot(
                day,
                "E",
            )
        )

        if len(endoscopy_entries) != 1:
            return ValidationResult(
                name="Endoscopy assignment",
                issues=[],
            )

        endoscopy_entry = endoscopy_entries[0]
        assigned_cases = []

        for case in cases:
            if case.anesthesiologist is None:
                continue

            identity = self.staff_identity_service.try_resolve(
                case.anesthesiologist
            )

            if (
                identity.resolved
                and identity.his_full_name == endoscopy_entry.person
            ):
                assigned_cases.append(case)

        endoscopy_cases = [
            case
            for case in assigned_cases
            if case.area == "ENDOSCOPIA"
        ]
        outside_endoscopy = [
            case
            for case in assigned_cases
            if case.area != "ENDOSCOPIA"
        ]
        issues = []

        if not endoscopy_cases:
            issues.append(
                f"{endoscopy_entry.person} has no ENDOSCOPIA cases"
            )

        if outside_endoscopy:
            issues.append(
                f"{endoscopy_entry.person} has "
                f"{len(outside_endoscopy)} case(s) outside ENDOSCOPIA"
            )

        return ValidationResult(
            name="Endoscopy assignment",
            issues=issues,
        )
