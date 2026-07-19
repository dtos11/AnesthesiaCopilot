from dataclasses import dataclass
from datetime import date

from app.models.call_assignment import CallAssignment
from app.models.obstetrics_assignment import ObstetricsAssignment
from app.models.patient_request import PatientRequest
from app.models.staff_state import StaffState
from app.models.vacation import Vacation
from app.models.availability_override import AvailabilityOverride


@dataclass(frozen=True)
class DepartmentState:
    date: date
    first_call: list[CallAssignment]
    second_call: list[CallAssignment]
    first_postcall: list[CallAssignment]
    second_postcall: list[CallAssignment]
    on_call: list[ObstetricsAssignment]
    postcall: list[ObstetricsAssignment]
    staff_states: list[StaffState]
    vacations: list[Vacation]
    availability_overrides: list[AvailabilityOverride]
    patient_requests: list[PatientRequest]
