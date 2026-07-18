from datetime import date, datetime, timedelta

from app.workbook_reader import WorkbookReader
from app.case_builder import CaseBuilder

from app.availability_reader import AvailabilityReader
from app.availability_service import AvailabilityService

from app.calendar.google_calendar_client import GoogleCalendarClient
from app.calendar.vacations_reader import VacationsReader
from app.guardias_reader import GuardiasReader
from app.guardias_service import GuardiasService
from app.maternidad_reader import MaternidadReader
from app.maternidad_service import MaternidadService

from app.privilege_reader import PrivilegeReader
from app.privilege_service import PrivilegeService

from app.incompatibility_reader import IncompatibilityReader
from app.incompatibility_service import IncompatibilityService

from app.reporting.console_report import ConsoleReport

from app.validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from app.validators.assigned_while_off import AssignedWhileOffValidator
from app.validators.assigned_while_ob_call import AssignedWhileObCallValidator
from app.validators.double_booking import DoubleBookingValidator
from app.validators.vte_lopez_privilege import VteLopezPrivilegeValidator
from app.validators.pediatrics_privilege import PediatricsPrivilegeValidator
from app.validators.surgeon_incompatibility import SurgeonIncompatibilityValidator


def main():

    schedule_date = date(2026, 7, 17)

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

    calendar_client = GoogleCalendarClient()

    vacations_reader = VacationsReader(calendar_client)

    availability_service = AvailabilityService(
        availability_reader,
        vacations_reader,
    )

    # ------------------------------------------------------------------
    # Guardias
    # ------------------------------------------------------------------

    guardias_service = GuardiasService(
        GuardiasReader(calendar_client)
    )

    previous_day_assignments = (
        guardias_service.get_assignments_for_date(
            schedule_date - timedelta(days=1)
        )
    )

    schedule_day_assignments = (
        guardias_service.get_assignments_for_date(schedule_date)
    )

    # ------------------------------------------------------------------
    # Maternidad
    # ------------------------------------------------------------------

    maternidad_service = MaternidadService(
        MaternidadReader(calendar_client)
    )

    previous_day_obstetrics_assignments = (
        maternidad_service.get_assignments_for_date(
            schedule_date - timedelta(days=1)
        )
    )

    schedule_day_obstetrics_assignments = (
        maternidad_service.get_assignments_for_date(schedule_date)
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

    assigned_while_ob_call_validator = AssignedWhileObCallValidator(
        maternidad_service
    )

    vte_lopez_validator = VteLopezPrivilegeValidator(
        privilege_service
    )

    pediatrics_validator = PediatricsPrivilegeValidator(
        privilege_service
    )

    double_booking_validator = DoubleBookingValidator()

    surgeon_incompatibility_validator = (
        SurgeonIncompatibilityValidator(
            incompatibility_service
        )
    )

    # ------------------------------------------------------------------
    # Run validations
    # ------------------------------------------------------------------

    missing_result = missing_validator.validate(cases)

    assigned_while_off_result = assigned_while_off_validator.validate(
        cases,
        date(2026, 7, 2)
    )

    assigned_while_ob_call_result = (
        assigned_while_ob_call_validator.validate(
            cases,
            schedule_date,
        )
    )

    vte_lopez_result = vte_lopez_validator.validate(cases)

    pediatrics_result = pediatrics_validator.validate(cases)

    double_booking_result = double_booking_validator.validate(cases)

    surgeon_incompatibility_result = (
        surgeon_incompatibility_validator.validate(cases)
    )

    # ------------------------------------------------------------------
    # Build report
    # ------------------------------------------------------------------

    report = ConsoleReport()

    report.title("AnesthesiaCopilot")

    report.field(
        "Schedule Date",
        schedule_date.strftime("%A %d %b %Y"),
    )

    report.field(
        "Generated",
        datetime.now().strftime("%A %d %b %Y %H:%M"),
    )

    report.blank()

    report.guardias(
        previous_day_assignments,
        schedule_day_assignments,
    )

    report.maternidad(
        previous_day_obstetrics_assignments,
        schedule_day_obstetrics_assignments,
    )

    report.heading("VALIDATION SUMMARY")

    report.field(
        "Scheduled procedures",
        len(cases),
    )

    report.field(
        missing_result.name,
        missing_result.issue_count,
    )

    report.field(
        assigned_while_off_result.name,
        assigned_while_off_result.issue_count,
    )

    report.field(
        assigned_while_ob_call_result.name,
        assigned_while_ob_call_result.issue_count,
    )

    report.field(
        double_booking_result.name,
        double_booking_result.issue_count,
    )

    report.field(
        surgeon_incompatibility_result.name,
        surgeon_incompatibility_result.issue_count,
    )

    report.field(
        vte_lopez_result.name,
        vte_lopez_result.issue_count,
    )

    report.field(
        pediatrics_result.name,
        pediatrics_result.issue_count,
    )

    report.heading("DETAILS")

    if missing_result.issue_count > 0:
        report.line(missing_result.name)
        report.separator()

        for case in missing_result.issues:
            report.line(str(case))

        report.blank()

    if assigned_while_off_result.issue_count > 0:
        report.line(assigned_while_off_result.name)
        report.separator()

        for case in assigned_while_off_result.issues:
            report.line(str(case))

        report.blank()

    if assigned_while_ob_call_result.issue_count > 0:
        report.line(assigned_while_ob_call_result.name)
        report.separator()

        for case in assigned_while_ob_call_result.issues:
            report.line(str(case))

        report.blank()

    if surgeon_incompatibility_result.issue_count > 0:
        report.line(surgeon_incompatibility_result.name)
        report.separator()

        for case in surgeon_incompatibility_result.issues:
            report.line(str(case))

        report.blank()

    if vte_lopez_result.issue_count > 0:
        report.line(vte_lopez_result.name)
        report.separator()

        for case in vte_lopez_result.issues:
            report.line(str(case))

        report.blank()

    if pediatrics_result.issue_count > 0:
        report.line(pediatrics_result.name)
        report.separator()

        for case in pediatrics_result.issues:
            report.line(str(case))

        report.blank()

    if double_booking_result.issue_count > 0:
        report.line(double_booking_result.name)
        report.separator()

        for current, next_case in double_booking_result.issues:
            report.line(f"DOUBLE BOOKING: {current.anesthesiologist}")
            report.line(str(current))
            report.line(str(next_case))
            report.blank()

    print(report.render())


if __name__ == "__main__":
    main()
