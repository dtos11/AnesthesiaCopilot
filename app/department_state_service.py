from datetime import date, timedelta

from app.availability_override_service import AvailabilityOverrideService
from app.availability_service import AvailabilityService
from app.guardias_service import GuardiasService
from app.maternidad_service import MaternidadService
from app.models.availability_override import AvailabilityOverride
from app.models.call_assignment import CallAssignment
from app.models.department_state import DepartmentState
from app.models.obstetrics_assignment import ObstetricsAssignment
from app.models.saturday_conflict import SaturdayConflict
from app.models.saturday_roster_entry import SaturdayRosterEntry
from app.models.staff_state import StaffState
from app.patient_request_service import PatientRequestService
from app.saturday_roster_service import SaturdayRosterService


class DepartmentStateService:

    def __init__(
        self,
        availability_service: AvailabilityService,
        guardias_service: GuardiasService,
        maternidad_service: MaternidadService,
        availability_override_service: AvailabilityOverrideService,
        patient_request_service: PatientRequestService,
        saturday_roster_service: SaturdayRosterService,
    ):
        self.availability_service = availability_service
        self.guardias_service = guardias_service
        self.maternidad_service = maternidad_service
        self.availability_override_service = availability_override_service
        self.patient_request_service = patient_request_service
        self.saturday_roster_service = saturday_roster_service

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
        vacations = self.availability_service.vacations_for(day)
        patient_requests = (
            self.patient_request_service.get_requests_for_date(day)
        )
        saturday_roster = (
            self.saturday_roster_service.get_entries_for_date(day)
            if day.weekday() == 5
            else []
        )
        staff_states = self._staff_states(
            day,
            vacations,
            on_call,
            overrides,
            saturday_roster,
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
            staff_states=staff_states,
            vacations=vacations,
            availability_overrides=overrides,
            patient_requests=patient_requests,
            saturday_conflicts=self._saturday_conflicts(
                saturday_roster,
                vacations,
                on_call,
                overrides,
            ),
        )

    def _staff_states(
        self,
        day: date,
        vacations,
        on_call: list[ObstetricsAssignment],
        overrides: list[AvailabilityOverride],
        saturday_roster: list[SaturdayRosterEntry],
    ) -> list[StaffState]:
        availability = self._baseline_availability(day, saturday_roster)
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

        if day.weekday() == 5:
            self._order_saturday_states(
                states,
                availability,
                obstetrics_people,
                overrides_by_person,
            )

        return states

    @staticmethod
    def _saturday_conflicts(
        saturday_roster: list[SaturdayRosterEntry],
        vacations,
        on_call: list[ObstetricsAssignment],
        overrides: list[AvailabilityOverride],
    ) -> list[SaturdayConflict]:
        vacation_people = {vacation.person for vacation in vacations}
        obstetrics_people = {assignment.person for assignment in on_call}
        override_people = {override.person for override in overrides}
        conflicts = []

        for entry in saturday_roster:
            if entry.person in vacation_people:
                final_state = "Vacaciones"
            elif entry.person in obstetrics_people:
                final_state = "OB"
            elif entry.person in override_people:
                final_state = "Modificación de disponibilidad"
            else:
                continue

            conflicts.append(
                SaturdayConflict(
                    slot=entry.slot,
                    staff=entry.person,
                    final_state=final_state,
                )
            )

        return conflicts

    def _order_saturday_states(
        self,
        states: list[StaffState],
        base_availability: dict,
        obstetrics_people: set[str],
        overrides_by_person: dict,
    ) -> None:
        slot_order = {
            slot: index
            for index, slot in enumerate(
                self.saturday_roster_service.OPERATIONAL_SLOT_ORDER
            )
        }
        weekly_order = {
            person: index
            for index, person in enumerate(self.availability_service.weekly)
        }

        def order_key(staff_state: StaffState):
            person = staff_state.person

            if staff_state.availability == "OFF":
                return 3, weekly_order.get(person, len(weekly_order))

            if person in obstetrics_people:
                return 1, 0

            base_slot = base_availability.get(person)

            if base_slot in slot_order:
                return 0, slot_order[base_slot]

            if person in overrides_by_person:
                return 2, weekly_order.get(person, len(weekly_order))

            return 3, weekly_order.get(person, len(weekly_order))

        states.sort(key=order_key)

    def _baseline_availability(
        self,
        day: date,
        saturday_roster: list[SaturdayRosterEntry],
    ) -> dict:
        if day.weekday() == 5:
            availability = {
                person: "OFF"
                for person in self.availability_service.weekly
            }

            for entry in saturday_roster:
                availability[entry.person] = entry.slot

            return availability

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
            return "OFF"

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
