from datetime import date

from app.workbook_reader import WorkbookReader
from app.case_builder import CaseBuilder

from app.availability_reader import AvailabilityReader
from app.availability_service import AvailabilityService

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.calendar.vacations_reader import VacationsReader

from app.privilege_reader import PrivilegeReader
from app.privilege_service import PrivilegeService

from app.incompatibility_reader import IncompatibilityReader
from app.incompatibility_service import IncompatibilityService

from app.validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from app.validators.assigned_while_off import AssignedWhileOffValidator
from app.validators.double_booking import DoubleBookingValidator
from app.validators.vte_lopez_privilege import VteLopezPrivilegeValidator
from app.validators.pediatrics_privilege import PediatricsPrivilegeValidator
from app.validators.surgeon_incompatibility import SurgeonIncompatibilityValidator

def main():

    print("=== AnesthesiaCopilot ===\n")

    # ------------------------------------------------------------------
    # Read schedule
    # ------------------------------------------------------------------

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")
    reader.read()

    builder = CaseBuilder(reader.workbook)
    cases = builder.build()

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    availability_reader = AvailabilityReader(
        "sample_data/weekly_availability_template.xlsx"
    )

    vacations_reader = VacationsReader(
        GoogleCalendarClient()
    )

    availability_service = AvailabilityService(
        availability_reader,
        vacations_reader,
    )

    # ------------------------------------------------------------------
    # Privileges
    # ------------------------------------------------------------------

    privilege_reader = PrivilegeReader(
        "sample_data/privilegios.xlsx"
    )

    privilege_service = PrivilegeService(
        privilege_reader
    )

    # ------------------------------------------------------------------
    # Incompatibilities
    # ------------------------------------------------------------------

    incompatibility_reader = IncompatibilityReader(
        "sample_data/privilegios.xlsx"
    )

    incompatibility_service = IncompatibilityService(
        incompatibility_reader
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    missing_validator = MissingAnesthesiologistValidator()

    assigned_while_off_validator = AssignedWhileOffValidator(
        availability_service
    )

    vte_lopez_validator = VteLopezPrivilegeValidator(
        privilege_service
    )

    pediatrics_validator = PediatricsPrivilegeValidator(
        privilege_service
    )

    double_booking_validator = DoubleBookingValidator()

    surgeon_incompatibility_validator = SurgeonIncompatibilityValidator(
        incompatibility_service
    )

    # ------------------------------------------------------------------
    # Run validations
    # ------------------------------------------------------------------

    missing_result = missing_validator.validate(cases)

    assigned_while_off_result = assigned_while_off_validator.validate(
        cases,
        date(2026, 7, 2)
    )

    vte_lopez_result = vte_lopez_validator.validate(cases)

    pediatrics_result = pediatrics_validator.validate(cases)

    double_booking_result = double_booking_validator.validate(cases)

    surgeon_incompatibility_result = (
        surgeon_incompatibility_validator.validate(cases)
    )

    # ------------------------------------------------------------------
    # Print results
    # ------------------------------------------------------------------

    print(f"\nFound {len(cases)} scheduled procedures\n")

    print(f"\n{missing_result.name}: {missing_result.issue_count}\n")

    for case in missing_result.issues:
        print(case)

    print(
        f"\n{vte_lopez_result.name}: "
        f"{vte_lopez_result.issue_count}\n"
    )

    for case in vte_lopez_result.issues:
        print(case)

    print(
        f"\n{pediatrics_result.name}: "
        f"{pediatrics_result.issue_count}\n"
    )

    for case in pediatrics_result.issues:
        print(case)

    print(
        f"\n{assigned_while_off_result.name}: "
        f"{assigned_while_off_result.issue_count}\n"
    )

    for case in assigned_while_off_result.issues:
        print(case)

    print(
        f"\n{surgeon_incompatibility_result.name}: "
        f"{surgeon_incompatibility_result.issue_count}\n"
    )

    for case in surgeon_incompatibility_result.issues:
        print(case)

    print(
        f"\n{double_booking_result.name}: "
        f"{double_booking_result.issue_count}\n"
    )

    for current, next_case in double_booking_result.issues:
        print(f"\nDOUBLE BOOKING: {current.anesthesiologist}")
        print(current)
        print(next_case)


if __name__ == "__main__":
    main()