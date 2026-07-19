from app.models.patient_request_match import PatientRequestMatch
from app.models.patient_request_violation import PatientRequestViolation
from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class PatientRequestValidator(Validator):

    def validate(
        self,
        matches: list[PatientRequestMatch],
    ) -> ValidationResult:
        violations = [
            PatientRequestViolation(match=match)
            for match in matches
            if match.request.requested_anesthesiologist
            != match.case.anesthesiologist
        ]

        return ValidationResult(
            name="Patient requests violated",
            issues=violations,
        )
