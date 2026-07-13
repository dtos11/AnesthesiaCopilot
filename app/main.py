from workbook_reader import WorkbookReader
from case_builder import CaseBuilder
from validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from validators.double_booking import DoubleBookingValidator
from availability_reader import AvailabilityReader

def main():
    print("=== AnesthesiaCopilot ===\n")

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")
    reader.read()

    builder = CaseBuilder(reader.workbook)
    cases = builder.build()   

    availability_reader = AvailabilityReader(reader.workbook)
    availability_reader.read()


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
