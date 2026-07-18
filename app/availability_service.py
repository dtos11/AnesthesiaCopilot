from datetime import date
import warnings

from app.availability_reader import AvailabilityReader
from app.calendar.vacations_reader import VacationsReader
from app.models.vacation import Vacation
from app.staff_identity_service import StaffIdentityService


class AvailabilityService:

    WEEKDAYS = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
    }

    def __init__(
        self,
        availability_reader: AvailabilityReader,
        vacations_reader: VacationsReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.availability_reader = availability_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()
        self.weekly = self._load_weekly_availability()
        self.vacations = self._load_vacations(vacations_reader)

    def available_on(self, day: date):

        weekly = self.weekly
        vacations = self.vacations

        weekday = self.WEEKDAYS[day.strftime("%A")]

        availability = {}

        # Build today's schedule from the weekly template
        for person, schedule in weekly.items():
            availability[person] = schedule[weekday]

        # Apply calendar overrides
        for vacation in vacations:

            if not vacation.includes(day):
                continue        

            original_shift = availability.get(vacation.person)

            availability[vacation.person] = "OFF"

            if vacation.replacement:
                availability[vacation.replacement] = original_shift

        return availability

    def availability_for(self, person: str, day: date):
        identity = self.staff_identity_service.try_resolve(person)

        if not identity.resolved:
            return None

        return self.available_on(day).get(identity.his_full_name)

    def _load_weekly_availability(self):
        weekly = {}

        for raw_name, schedule in self.availability_reader.read().items():
            identity = self.staff_identity_service.try_resolve(raw_name)

            if not identity.resolved:
                self._warn_unknown(raw_name, "availability")
                continue

            weekly[identity.his_full_name] = schedule

        return weekly

    def _load_vacations(self, vacations_reader: VacationsReader):
        vacations = []

        for vacation in vacations_reader.read():
            person = self._resolve_source_name(
                vacation.person,
                "vacations",
            )

            if person is None:
                continue

            replacement = None

            if vacation.replacement:
                replacement = self._resolve_source_name(
                    vacation.replacement,
                    "vacations",
                )

            vacations.append(
                Vacation(
                    person=person,
                    start=vacation.start,
                    end=vacation.end,
                    replacement=replacement,
                    needs_replacement=vacation.needs_replacement,
                )
            )

        return vacations

    def _resolve_source_name(self, raw_name: str, source: str):
        identity = self.staff_identity_service.try_resolve(raw_name)

        if identity.resolved:
            return identity.his_full_name

        self._warn_unknown(raw_name, source)
        return None

    def _warn_unknown(self, raw_name: str, source: str) -> None:
        warning_key = (source, str(raw_name).strip().casefold())

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        warnings.warn(
            f"Unresolved staff identity from {source}: '{raw_name}'",
            stacklevel=2,
        )
