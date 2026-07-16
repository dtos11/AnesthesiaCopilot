from app.validators.validator import Validator
from app.models.validation_result import ValidationResult


class PediatricsPrivilegeValidator(Validator):

    PEDIATRIC_AGE_LIMIT = 8

    def __init__(self, privilege_service):
        self.privilege_service = privilege_service

    def validate(self, cases):

        errors = []

        for case in cases:

            if case.patient_age_years is None:
                continue

            if case.patient_age_years >= self.PEDIATRIC_AGE_LIMIT:
                continue

            if case.anesthesiologist is None:
                continue

            if self.privilege_service.has(
                case.anesthesiologist,
                "Pediátricos",
            ):
                continue

            errors.append(case)

        return ValidationResult(
            name="Pediatrics privilege",
            issues=errors,
        )