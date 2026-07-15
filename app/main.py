from app.workbook_reader import WorkbookReader
from app.case_builder import CaseBuilder
from app.availability_reader import AvailabilityReader
from app.validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from app.validators.double_booking import DoubleBookingValidator

from datetime import date

from app.availability_service import AvailabilityService
from app.calendar.google_calendar_client import GoogleCalendarClient
from app.calendar.vacations_reader import VacationsReader

def main():
    print("=== AnesthesiaCopilot ===\n")

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")
    reader.read()

    builder = CaseBuilder(reader.workbook)
    cases = builder.build()   

    availability_reader = AvailabilityReader(
        "sample_data/weekly_availability_template.xlsx"
)

    vacations_reader = VacationsReader(
        GoogleCalendarClient()
)
    vacations = vacations_reader.read()    

    availability_service = AvailabilityService(
        availability_reader,
        vacations_reader,
)

    today = availability_service.available_on(date.today())

    print(f"\nFound {len(cases)} scheduled procedures\n")

    missing_validator = MissingAnesthesiologistValidator()

    missing_result = missing_validator.validate(cases)

    print(f"\n{missing_result.name}: {missing_result.issue_count}\n")

    for case in missing_result.issues:
        print(case)

    double_booking_validator = DoubleBookingValidator()

    double_booking_result = double_booking_validator.validate(cases)

    print(f"\n{double_booking_result.name}: {double_booking_result.issue_count}\n")

    for current, next_case in double_booking_result.issues:
        print(f"\nDOUBLE BOOKING: {current.anesthesiologist}")
        print(current)
        print(next_case)


if __name__ == "__main__":
    main()
