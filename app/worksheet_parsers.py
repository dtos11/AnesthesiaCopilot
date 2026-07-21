import re
from datetime import date

from app.models.case import Case
from app.staff_identity_service import StaffIdentityService


def _normalize_header(value) -> str:
    return str(value).strip().casefold()


class ScheduleSheetParser:

    def __init__(self, staff_identity_service: StaffIdentityService):
        self.staff_identity_service = staff_identity_service

    def _parse_anesthesiologist(
        self,
        raw_value,
    ) -> tuple[str | None, str | None]:
        if raw_value is None or not str(raw_value).strip():
            return None, None

        value = str(raw_value).strip()
        words = list(re.finditer(r"\S+", value))

        for word in reversed(words):
            raw_person = value[:word.end()]
            identity = self.staff_identity_service.try_resolve(raw_person)

            if not identity.resolved:
                continue

            notation = value[word.end():].strip() or None
            return identity.his_full_name, notation

        return value, None


class StandardScheduleSheetParser(ScheduleSheetParser):

    REQUIRED_HEADERS = {
        "sala (denominación breve)",
        "hora planificada",
        "duración",
        "paciente/sexo/edad",
        "cirujano",
        "anestesia",
    }

    def can_parse(self, sheet) -> bool:
        headers = self._headers(sheet)
        return self.REQUIRED_HEADERS.issubset(headers)

    def parse(self, sheet, schedule_date: date) -> list[Case]:
        headers = self._headers(sheet)
        cases = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            operating_room = row[headers["sala (denominación breve)"]]

            if operating_room is None:
                continue

            anesthesiologist, notation = self._parse_anesthesiologist(
                row[headers["anestesia"]]
            )
            anesthesia_type = "SEDACIÓN"

            if "tipo de anestesia" in headers:
                anesthesia_type = row[headers["tipo de anestesia"]]

            duration = row[headers["duración"]]
            cases.append(
                Case(
                    date=schedule_date,
                    area=sheet.title.strip(),
                    operating_room=operating_room,
                    scheduled_time=row[headers["hora planificada"]],
                    duration_minutes=int(duration) if duration else None,
                    patient=row[headers["paciente/sexo/edad"]],
                    surgeon=row[headers["cirujano"]],
                    anesthesia_type=anesthesia_type,
                    anesthesiologist=anesthesiologist or None,
                    anesthesiologist_notation=notation,
                )
            )

        return cases

    @staticmethod
    def _headers(sheet) -> dict[str, int]:
        header_row = next(
            sheet.iter_rows(
                min_row=1,
                max_row=1,
                values_only=True,
            ),
            (),
        )
        return {
            _normalize_header(value): index
            for index, value in enumerate(header_row)
            if value is not None
        }


class ImagingScheduleSheetParser(ScheduleSheetParser):

    REQUIRED_HEADERS = {
        "hora",
        "tratamiento",
        "paciente",
        "anestesia",
    }
    HEADER_SEARCH_LIMIT = 10

    def can_parse(self, sheet) -> bool:
        return self._find_headers(sheet) is not None

    def parse(self, sheet, schedule_date: date) -> list[Case]:
        header_details = self._find_headers(sheet)

        if header_details is None:
            return []

        header_row_number, headers = header_details
        operating_room = self._worksheet_label(sheet, header_row_number)
        cases = []

        for row in sheet.iter_rows(
            min_row=header_row_number + 1,
            values_only=True,
        ):
            scheduled_time = row[headers["hora"]]

            if scheduled_time is None:
                continue

            anesthesiologist, notation = self._parse_anesthesiologist(
                row[headers["anestesia"]]
            )
            cases.append(
                Case(
                    date=schedule_date,
                    area=sheet.title.strip(),
                    operating_room=operating_room,
                    scheduled_time=scheduled_time,
                    duration_minutes=0,
                    patient=row[headers["paciente"]],
                    surgeon="",
                    anesthesia_type="",
                    anesthesiologist=anesthesiologist or None,
                    anesthesiologist_notation=notation,
                )
            )

        return cases

    def _find_headers(self, sheet) -> tuple[int, dict[str, int]] | None:
        for row_number, row in enumerate(
            sheet.iter_rows(
                min_row=1,
                max_row=min(sheet.max_row, self.HEADER_SEARCH_LIMIT),
                values_only=True,
            ),
            start=1,
        ):
            headers = {
                _normalize_header(value): index
                for index, value in enumerate(row)
                if value is not None
            }

            if self.REQUIRED_HEADERS.issubset(headers):
                return row_number, headers

        return None

    @staticmethod
    def _worksheet_label(sheet, header_row_number: int) -> str:
        if header_row_number <= 1:
            return sheet.title.strip()

        for row in sheet.iter_rows(
            min_row=1,
            max_row=header_row_number - 1,
            values_only=True,
        ):
            for value in row:
                if value is not None and str(value).strip():
                    return str(value).strip()

        return sheet.title.strip()
