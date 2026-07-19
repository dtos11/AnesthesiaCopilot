import re
from datetime import date

from app.models.case import Case
from app.staff_identity_service import StaffIdentityService


class CaseBuilder:

    def __init__(
        self,
        workbook,
        schedule_date: date,
        staff_identity_service: StaffIdentityService,
    ):
        self.workbook = workbook
        self.schedule_date = schedule_date
        self.staff_identity_service = staff_identity_service

    def build(self):

        cases = []

        for sheet_name in self.workbook.sheetnames:
            area = sheet_name.strip()

            if area == "DISPONIBILIDAD":
                continue

            sheet = self.workbook[sheet_name]

            for row in sheet.iter_rows(min_row=2, values_only=True):

                if row[0] is None:
                    continue

                

                if area == "ENDOSCOPIA":
                    anesthesia_type = "SEDACIÓN"
                    anesthesiologist = row[8]
                else:
                    anesthesia_type = row[6]
                    anesthesiologist = row[9]

                (
                    anesthesiologist,
                    anesthesiologist_notation,
                ) = self._parse_anesthesiologist(anesthesiologist)

                case = Case(
                    date=self.schedule_date,
                    area=area,
                    operating_room=row[0],
                    scheduled_time=row[1],
                    duration_minutes=int(row[2]) if row[2] else None,
                    patient=row[4],
                    surgeon=row[5],
                    anesthesia_type=anesthesia_type,
                    anesthesiologist=anesthesiologist or None,
                    anesthesiologist_notation=anesthesiologist_notation,
                )

                cases.append(case)

        return cases

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
