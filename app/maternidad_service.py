from datetime import date

from app.maternidad_reader import MaternidadReader
from app.models.obstetrics_assignment import ObstetricsAssignment


class MaternidadService:

    def __init__(self, maternidad_reader: MaternidadReader):
        self.maternidad_reader = maternidad_reader

    def get_assignments_for_date(
        self,
        day: date,
    ) -> list[ObstetricsAssignment]:
        return self.maternidad_reader.read(day)

    def is_assigned(self, person: str, day: date) -> bool:
        expected = self._normalize(person)

        return any(
            self._normalize(assignment.person) == expected
            for assignment in self.get_assignments_for_date(day)
        )

    @staticmethod
    def _normalize(person: str) -> str:
        return " ".join(person.split()).casefold()
