from app.validators.validator import Validator
from app.models.validation_result import ValidationResult


class VteLopezPrivilegeValidator(Validator):

    def __init__(self, privilege_service):
        self.privilege_service = privilege_service

    def validate(self, cases):

        errors = []

        for case in cases:

            if case.area != "VTE LOPEZ":
                continue

            if case.anesthesiologist is None:
                continue

            if self.privilege_service.has(case.anesthesiologist):
                continue

            errors.append(case)

        return ValidationResult(
            name="VTE Lopez privilege",
            issues=errors,
        )