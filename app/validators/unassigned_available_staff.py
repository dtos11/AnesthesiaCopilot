from app.models.validation_result import ValidationResult
from app.validators.validator import Validator


class UnassignedAvailableStaffValidator(Validator):

    def validate(self, cases, department_state):
        assigned_people = {
            case.anesthesiologist
            for case in cases
            if case.anesthesiologist is not None
        }
        vacation_people = {
            vacation.person
            for vacation in department_state.vacations
        }
        issues = [
            staff_state
            for staff_state in department_state.staff_states
            if staff_state.person not in assigned_people
            and staff_state.person not in vacation_people
            and self._is_available(staff_state.availability)
        ]

        return ValidationResult(
            name="Unassigned available staff",
            issues=issues,
        )

    @staticmethod
    def _is_available(availability) -> bool:
        if availability is None:
            return False

        if isinstance(availability, list):
            instructions = {
                str(instruction).strip().casefold()
                for instruction in availability
                if str(instruction).strip()
            }
            return bool(instructions) and "off" not in instructions

        value = str(availability).strip().casefold()
        return bool(value) and value not in {"off", "ob"}
