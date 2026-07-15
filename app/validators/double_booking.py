from app.validators.validator import Validator
from app.models.validation_result import ValidationResult


class DoubleBookingValidator(Validator):

    def validate(self, cases):

        assignments = {}

        for case in cases:

            if case.anesthesiologist is None:
                continue

            if case.anesthesiologist not in assignments:
                assignments[case.anesthesiologist] = []

            assignments[case.anesthesiologist].append(case)

        errors = []

        for anesthesiologist, assigned_cases in assignments.items():

            assigned_cases.sort(key=lambda case: case.scheduled_time)

            for i in range(len(assigned_cases) - 1):

                current = assigned_cases[i]
                next_case = assigned_cases[i + 1]

                if current.end_time() > next_case.scheduled_time:

                    if current.is_same_procedure(next_case):
                        continue                    

                    errors.append((current, next_case))

        return ValidationResult(
            name="Double bookings",
            issues=errors,
)