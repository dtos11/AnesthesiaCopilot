from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class SaturdayRosterCalendarIntegrityValidator(Validator):

    def __init__(self, saturday_roster_service):
        self.saturday_roster_service = saturday_roster_service

    def validate(self, cases, day):
        endoscopy_entries = (
            self.saturday_roster_service.get_entries_for_slot(
                day,
                "E",
            )
        )

        issues = []

        if len(endoscopy_entries) != 1:
            issues.append(endoscopy_entries)

        return ValidationResult(
            name="Saturday roster calendar integrity",
            issues=issues,
        )
