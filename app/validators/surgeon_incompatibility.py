from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class SurgeonIncompatibilityValidator(Validator):

    def __init__(self, incompatibility_service):
        self.incompatibility_service = incompatibility_service

    def validate(self, cases):

        errors = []

        for case in cases:

            if case.anesthesiologist is None:
                continue

            if self.incompatibility_service.has(
                case.anesthesiologist,
                case.surgeon,
            ):
                errors.append(case)

        return ValidationResult(
            name="Surgeon incompatibilities",
            issues=errors,
        )