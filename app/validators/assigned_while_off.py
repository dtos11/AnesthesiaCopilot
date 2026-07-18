from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class AssignedWhileOffValidator(Validator):

    def __init__(self, availability_service):
        self.availability_service = availability_service

    def validate(self, cases, day):

        issues = []

        for case in cases:

            if case.anesthesia_type == "ANESTESIA LOCAL":
                continue

            if case.anesthesiologist is None:
                continue

            if (
                self.availability_service.availability_for(
                    case.anesthesiologist,
                    day,
                )
                == "OFF"
            ):
                issues.append(case)

        return ValidationResult(
            name="Assigned while OFF",
            issues=issues,
        )
