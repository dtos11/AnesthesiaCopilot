from openpyxl import load_workbook


class AvailabilityReader:

    def __init__(self, filename: str):
        self.filename = filename

    def read(self):

        workbook = load_workbook(self.filename)

        sheet = workbook["Weekly Availability"]

        headers = [cell.value for cell in sheet[1]]

        availability = {}

        for row in sheet.iter_rows(min_row=2, values_only=True):

            if not row[0]:
                continue

            person = row[0]

            availability[person] = {}

            for i in range(1, len(headers)):
                if headers[i] is None:
                    continue

                availability[person][headers[i]] = row[i]

        return availability