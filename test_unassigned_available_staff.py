import unittest
from types import SimpleNamespace

from app.models.staff_state import StaffState
from app.validators.unassigned_available_staff import (
    UnassignedAvailableStaffValidator,
)


class UnassignedAvailableStaffValidatorTests(unittest.TestCase):

    def setUp(self):
        self.validator = UnassignedAvailableStaffValidator()

    def test_reports_only_available_staff_without_cases(self):
        department_state = SimpleNamespace(
            staff_states=[
                StaffState("Weekday Available", "08:00-20:00"),
                StaffState("Saturday Available", "Q3C"),
                StaffState("Assigned", "08:30-20:00"),
                StaffState("Off", "OFF"),
                StaffState("Obstetrics", "OB"),
                StaffState("Vacation", "08:00-20:00"),
                StaffState("Override Off", ["OFF"]),
                StaffState("Empty Override", []),
            ],
            vacations=[SimpleNamespace(person="Vacation")],
        )
        cases = [SimpleNamespace(anesthesiologist="Assigned")]

        result = self.validator.validate(cases, department_state)

        self.assertEqual(
            [state.person for state in result.issues],
            ["Weekday Available", "Saturday Available"],
        )

    def test_non_off_override_is_available(self):
        department_state = SimpleNamespace(
            staff_states=[
                StaffState("Timed Override", ["13:00-20:00"]),
                StaffState("Area Override", ["ENDOSCOPY"]),
            ],
            vacations=[],
        )

        result = self.validator.validate([], department_state)

        self.assertEqual(result.issue_count, 2)


if __name__ == "__main__":
    unittest.main()
