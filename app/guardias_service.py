from datetime import date

from app.guardias_reader import GuardiasReader
from app.models.call_assignment import CallAssignment


class GuardiasService:

    def __init__(self, guardias_reader: GuardiasReader):
        self.guardias_reader = guardias_reader

    def get_assignments_for_date(self, day: date) -> list[CallAssignment]:
        return self.guardias_reader.read(
            start_date=day,
            end_date=day,
        )
