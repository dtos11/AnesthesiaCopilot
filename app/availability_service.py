from datetime import date

from app.availability_reader import AvailabilityReader
from app.calendar.vacations_reader import VacationsReader


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
    ):
        self.availability_reader = availability_reader
        self.vacations_reader = vacations_reader

    def available_on(self, day: date):

        weekly = self.availability_reader.read()
        vacations = self.vacations_reader.read()

        weekday = self.WEEKDAYS[day.strftime("%A")]

        availability = {}

        # Build today's schedule from the weekly template
        for person, schedule in weekly.items():
            availability[person] = schedule[weekday]

        # Apply calendar overrides
        for vacation in vacations:

            if not vacation.includes(vacation.person, day):
                continue

            original_shift = availability.get(vacation.person)

            availability[vacation.person] = "OFF"

            if vacation.replacement:
                availability[vacation.replacement] = original_shift

        return availability