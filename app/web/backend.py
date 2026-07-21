from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.availability_override_service import AvailabilityOverrideService
from app.availability_overrides_reader import AvailabilityOverridesReader
from app.availability_reader import AvailabilityReader
from app.availability_service import AvailabilityService
from app.calendar.google_calendar_client import GoogleCalendarClient
from app.calendar.vacations_reader import VacationsReader
from app.case_builder import CaseBuilder
from app.department_state_service import DepartmentStateService
from app.guardias_reader import GuardiasReader
from app.guardias_service import GuardiasService
from app.incompatibility_reader import IncompatibilityReader
from app.incompatibility_service import IncompatibilityService
from app.maternidad_reader import MaternidadReader
from app.maternidad_service import MaternidadService
from app.patient_request_matcher import PatientRequestMatcher
from app.patient_request_service import PatientRequestService
from app.patient_requests_reader import PatientRequestsReader
from app.privilege_reader import PrivilegeReader
from app.privilege_service import PrivilegeService
from app.saturday_roster_reader import SaturdayRosterReader
from app.saturday_roster_service import SaturdayRosterService
from app.schedule_date_inference import infer_schedule_date
from app.staff_directory_reader import StaffDirectoryReader
from app.staff_identity_service import StaffIdentityService
from app.validators.assigned_while_ob_call import AssignedWhileObCallValidator
from app.validators.assigned_while_off import AssignedWhileOffValidator
from app.validators.double_booking import DoubleBookingValidator
from app.validators.endoscopy_assignment import EndoscopyAssignmentValidator
from app.validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from app.validators.patient_request import PatientRequestValidator
from app.validators.pediatrics_privilege import PediatricsPrivilegeValidator
from app.validators.saturday_assignments_outside_roster import (
    SaturdayAssignmentsOutsideRosterValidator,
)
from app.validators.saturday_roster_calendar_integrity import (
    SaturdayRosterCalendarIntegrityValidator,
)
from app.validators.surgeon_incompatibility import SurgeonIncompatibilityValidator
from app.validators.vte_lopez_privilege import VteLopezPrivilegeValidator
from app.workbook_reader import WorkbookReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA = PROJECT_ROOT / "sample_data"


@dataclass(frozen=True)
class DepartmentStateView:
    state: object
    staff_states: list


@dataclass(frozen=True)
class ValidationView:
    date: date
    cases: list
    missing: object
    assigned_while_off: object | None
    assigned_while_ob_call: object
    double_booking: object
    incompatibilities: object
    vte_lopez: object
    pediatrics: object
    patient_requests: object
    saturday_calendar_integrity: object | None
    endoscopy_assignment: object | None
    saturday_outside_roster: object | None


class WebBackend:

    def __init__(self):
        self.staff_identity_service = StaffIdentityService(
            StaffDirectoryReader(SAMPLE_DATA / "department_staff.xlsx")
        )
        self.calendar_client = GoogleCalendarClient()
        self.availability_service = AvailabilityService(
            AvailabilityReader(
                SAMPLE_DATA / "weekly_availability_template.xlsx"
            ),
            VacationsReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.maternidad_service = MaternidadService(
            MaternidadReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.guardias_service = GuardiasService(
            GuardiasReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.availability_override_service = AvailabilityOverrideService(
            AvailabilityOverridesReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.patient_request_service = PatientRequestService(
            PatientRequestsReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.department_state_service = DepartmentStateService(
            self.availability_service,
            self.guardias_service,
            self.maternidad_service,
            self.availability_override_service,
            self.patient_request_service,
        )
        privilege_service = PrivilegeService(
            PrivilegeReader(SAMPLE_DATA / "privilegios.xlsx"),
            self.staff_identity_service,
        )
        incompatibility_service = IncompatibilityService(
            IncompatibilityReader(SAMPLE_DATA / "privilegios.xlsx"),
            self.staff_identity_service,
        )
        self.saturday_roster_service = SaturdayRosterService(
            SaturdayRosterReader(self.calendar_client),
            self.staff_identity_service,
        )
        self.missing_validator = MissingAnesthesiologistValidator()
        self.assigned_while_off_validator = AssignedWhileOffValidator(
            self.availability_service
        )
        self.assigned_while_ob_call_validator = AssignedWhileObCallValidator(
            self.maternidad_service
        )
        self.double_booking_validator = DoubleBookingValidator()
        self.incompatibility_validator = SurgeonIncompatibilityValidator(
            incompatibility_service
        )
        self.vte_lopez_validator = VteLopezPrivilegeValidator(
            privilege_service
        )
        self.pediatrics_validator = PediatricsPrivilegeValidator(
            privilege_service
        )
        self.patient_request_validator = PatientRequestValidator()
        self.saturday_integrity_validator = (
            SaturdayRosterCalendarIntegrityValidator(
                self.saturday_roster_service
            )
        )
        self.endoscopy_validator = EndoscopyAssignmentValidator(
            self.saturday_roster_service,
            self.staff_identity_service,
        )
        self.saturday_outside_roster_validator = (
            SaturdayAssignmentsOutsideRosterValidator(
                self.saturday_roster_service,
                self.staff_identity_service,
            )
        )

    def department_state_for(self, day: date) -> DepartmentStateView:
        state = self.department_state_service.get_state_for_date(day)
        order = {
            person: index
            for index, person in enumerate(self.availability_service.weekly)
        }
        staff_states = sorted(
            enumerate(state.staff_states),
            key=lambda item: order.get(
                item[1].person,
                len(order) + item[0],
            ),
        )
        return DepartmentStateView(
            state=state,
            staff_states=[item for _, item in staff_states],
        )

    def validate_workbook(self, workbook_path: str) -> ValidationView:
        schedule_date = infer_schedule_date(workbook_path)
        reader = WorkbookReader(workbook_path)
        reader.read()
        cases = CaseBuilder(
            reader.workbook,
            schedule_date,
            self.staff_identity_service,
        ).build()
        department_state = self.department_state_service.get_state_for_date(
            schedule_date
        )
        assigned_while_off = None

        if schedule_date.weekday() != 5:
            assigned_while_off = self.assigned_while_off_validator.validate(
                cases,
                schedule_date,
            )

        saturday_integrity = None
        endoscopy_assignment = None
        saturday_outside_roster = None

        if schedule_date.weekday() == 5:
            saturday_integrity = self.saturday_integrity_validator.validate(
                cases,
                schedule_date,
            )

            if saturday_integrity.passed:
                endoscopy_assignment = self.endoscopy_validator.validate(
                    cases,
                    schedule_date,
                )

            saturday_outside_roster = (
                self.saturday_outside_roster_validator.validate(
                    cases,
                    schedule_date,
                )
            )

        patient_matches = PatientRequestMatcher().match(
            department_state.patient_requests,
            cases,
        )
        return ValidationView(
            date=schedule_date,
            cases=cases,
            missing=self.missing_validator.validate(cases),
            assigned_while_off=assigned_while_off,
            assigned_while_ob_call=(
                self.assigned_while_ob_call_validator.validate(
                    cases,
                    schedule_date,
                )
            ),
            double_booking=self.double_booking_validator.validate(cases),
            incompatibilities=self.incompatibility_validator.validate(cases),
            vte_lopez=self.vte_lopez_validator.validate(cases),
            pediatrics=self.pediatrics_validator.validate(cases),
            patient_requests=self.patient_request_validator.validate(
                patient_matches
            ),
            saturday_calendar_integrity=saturday_integrity,
            endoscopy_assignment=endoscopy_assignment,
            saturday_outside_roster=saturday_outside_roster,
        )
