from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class AssignedWhileObCallValidator(Validator):

    def __init__(self, maternidad_service):
        self.maternidad_service = maternidad_service

    def validate(self, cases, day):
        issues = []

        for case in cases:
            if case.anesthesiologist is None:
                continue

            if self.maternidad_service.is_assigned(
                case.anesthesiologist,
                day,
            ):
                issues.append(case)

        return ValidationResult(
            name="Assigned while OB call",
            issues=issues,
        )
