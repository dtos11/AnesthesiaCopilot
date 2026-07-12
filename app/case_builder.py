from models.case import Case


class CaseBuilder:

    def __init__(self, workbook):
        self.workbook = workbook

    def build(self):

        cases = []

        for sheet_name in self.workbook.sheetnames:

            if sheet_name == "DISPONIBILIDAD":
                continue

            sheet = self.workbook[sheet_name]

            for row in sheet.iter_rows(min_row=2, values_only=True):

                if row[0] is None:
                    continue

                

                if sheet_name == "ENDOSCOPIA":
                    anesthesia_type = "SEDACIÓN"
                    anesthesiologist = row[8]
                else:
                    anesthesia_type = row[6]
                    anesthesiologist = row[9]

                case = Case(
    area=sheet_name,
    operating_room=row[0],
    scheduled_time=row[1],
    duration_minutes=int(row[2]) if row[2] else None,
    patient=row[4],
    surgeon=row[5],
    anesthesia_type=anesthesia_type,
    anesthesiologist=anesthesiologist or None,
)

                cases.append(case)

        return cases