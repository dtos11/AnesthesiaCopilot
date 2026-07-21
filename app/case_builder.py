from datetime import date

from app.staff_identity_service import StaffIdentityService
from app.worksheet_parsers import (
    ImagingScheduleSheetParser,
    StandardScheduleSheetParser,
)


class CaseBuilder:

    def __init__(
        self,
        workbook,
        schedule_date: date,
        staff_identity_service: StaffIdentityService,
        parsers=None,
    ):
        self.workbook = workbook
        self.schedule_date = schedule_date
        self.parsers = (
            parsers
            if parsers is not None
            else [
                StandardScheduleSheetParser(staff_identity_service),
                ImagingScheduleSheetParser(staff_identity_service),
            ]
        )

    def build(self):

        cases = []

        for sheet_name in self.workbook.sheetnames:
            sheet = self.workbook[sheet_name]
            parser = next(
                (
                    candidate
                    for candidate in self.parsers
                    if candidate.can_parse(sheet)
                ),
                None,
            )

            if parser is None:
                print(
                    f'Skipping worksheet "{sheet_name}" '
                    "(unrecognized worksheet)"
                )
                continue

            cases.extend(parser.parse(sheet, self.schedule_date))

        return cases
