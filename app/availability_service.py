from datetime import date
import re
import warnings

from app.availability_reader import AvailabilityReader
from app.calendar.vacations_reader import VacationsReader
from app.models.vacation import Vacation
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


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

            covered_person = self._covered_person(vacation.notation)

            if covered_person is not None:
                availability[covered_person] = original_shift

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
            parsed_vacation = self._parse_vacation(vacation)

            if parsed_vacation is None:
                continue

            person = self.staff_identity_service.resolve(
                parsed_vacation.person
            )
            vacations.append(
                Vacation(
                    person=person,
                    start=parsed_vacation.start,
                    end=parsed_vacation.end,
                    notation=parsed_vacation.notation,
                )
            )

        return vacations

    def _parse_vacation(self, vacation: Vacation) -> Vacation | None:
        summary = vacation.person.strip()
        words = list(re.finditer(r"\S+", summary))

        for word in reversed(words):
            raw_person = summary[:word.end()]
            identity = self.staff_identity_service.try_resolve(raw_person)

            if not identity.resolved:
                continue

            notation = summary[word.end():].strip() or None
            return Vacation(
                person=raw_person,
                start=vacation.start,
                end=vacation.end,
                notation=notation,
            )

        self._warn_unknown(summary, "vacations")
        return None

    def _covered_person(self, notation: str | None) -> str | None:
        prefix = "cubre "

        if notation is None or not notation.startswith(prefix):
            return None

        identity = self.staff_identity_service.try_resolve(
            notation[len(prefix):].strip()
        )
        return identity.his_full_name

    def _warn_unknown(self, raw_name: str, source: str) -> None:
        warning_key = (source, str(raw_name).strip().casefold())

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = f"Unresolved staff identity from {source}: '{raw_name}'"
        warnings.warn(
            unresolved_staff_message(
                message,
                raw_name,
                self.staff_identity_service,
            ),
            stacklevel=2,
        )
