from app.availability_reader import AvailabilityReader
from app.calendar.vacations_reader import VacationsReader


class AvailabilityService:

    def __init__(
        self,
        availability_reader: AvailabilityReader,
        vacations_reader: VacationsReader,
    ):
        self.availability_reader = availability_reader
        self.vacations_reader = vacations_reader