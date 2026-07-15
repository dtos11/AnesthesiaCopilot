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
        self.weekly = availability_reader.read()
        self.vacations = vacations_reader.read()

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