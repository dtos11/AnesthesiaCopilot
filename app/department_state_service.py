from datetime import date, timedelta

from app.availability_override_service import AvailabilityOverrideService
from app.availability_service import AvailabilityService
from app.guardias_service import GuardiasService
from app.maternidad_service import MaternidadService
from app.models.availability_override import AvailabilityOverride
from app.models.call_assignment import CallAssignment
from app.models.department_state import DepartmentState
from app.models.obstetrics_assignment import ObstetricsAssignment
from app.models.staff_state import StaffState
from app.patient_request_service import PatientRequestService


class DepartmentStateService:

    def __init__(
        self,
        availability_service: AvailabilityService,
        guardias_service: GuardiasService,
        maternidad_service: MaternidadService,
        availability_override_service: AvailabilityOverrideService,
        patient_request_service: PatientRequestService,
    ):
        self.availability_service = availability_service
        self.guardias_service = guardias_service
        self.maternidad_service = maternidad_service
        self.availability_override_service = availability_override_service
        self.patient_request_service = patient_request_service

    def get_state_for_date(self, day: date) -> DepartmentState:
        previous_day = day - timedelta(days=1)
        call_assignments = (
            self.guardias_service.get_assignments_for_date(day)
        )
        postcall_assignments = (
            self.guardias_service.get_assignments_for_date(previous_day)
        )
        on_call = self.maternidad_service.get_assignments_for_date(day)
        postcall = self.maternidad_service.get_assignments_for_date(
            previous_day
        )
        overrides = (
            self.availability_override_service.get_overrides_for_date(day)
        )
        vacations = [
            vacation
            for vacation in self.availability_service.vacations
            if vacation.includes(day)
        ]
        patient_requests = (
            self.patient_request_service.get_requests_for_date(day)
        )

        return DepartmentState(
            date=day,
            first_call=self._call_assignments(call_assignments, role=1),
            second_call=self._call_assignments(call_assignments, role=2),
            first_postcall=self._call_assignments(
                postcall_assignments,
                role=1,
            ),
            second_postcall=self._call_assignments(
                postcall_assignments,
                role=2,
            ),
            on_call=on_call,
            postcall=postcall,
            staff_states=self._staff_states(
                day,
                vacations,
                on_call,
                overrides,
            ),
            vacations=vacations,
            availability_overrides=overrides,
            patient_requests=patient_requests,
        )

    def _staff_states(
        self,
        day: date,
        vacations,
        on_call: list[ObstetricsAssignment],
        overrides: list[AvailabilityOverride],
    ) -> list[StaffState]:
        availability = self._baseline_availability(day)
        people = set(availability)
        people.update(vacation.person for vacation in vacations)
        people.update(assignment.person for assignment in on_call)
        people.update(override.person for override in overrides)

        vacation_people = {vacation.person for vacation in vacations}
        obstetrics_people = {assignment.person for assignment in on_call}
        overrides_by_person = {
            override.person: override
            for override in overrides
        }

        states = []

        for person in sorted(people):
            effective_availability = availability.get(person)

            if person in vacation_people:
                effective_availability = "OFF"
            elif person in obstetrics_people:
                effective_availability = "OB"
            elif person in overrides_by_person:
                effective_availability = (
                    overrides_by_person[person].instructions
                )

            states.append(
                StaffState(
                    person=person,
                    availability=effective_availability,
                )
            )

        return states

    def _baseline_availability(self, day: date) -> dict:
        weekday = self.availability_service.WEEKDAYS.get(
            day.strftime("%A")
        )

        if weekday is None:
            return {
                person: None
                for person in self.availability_service.weekly
            }

        return {
            person: self._without_weekly_ob(schedule[weekday])
            for person, schedule in self.availability_service.weekly.items()
        }

    @staticmethod
    def _without_weekly_ob(availability):
        if (
            isinstance(availability, str)
            and availability.strip().casefold() == "ob"
        ):
            return None

        return availability

    @staticmethod
    def _call_assignments(
        assignments: list[CallAssignment],
        role: int,
    ) -> list[CallAssignment]:
        return [
            assignment
            for assignment in assignments
            if assignment.role == role
        ]
