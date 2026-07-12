from workbook_reader import WorkbookReader
from case_builder import CaseBuilder
from validators.missing_anesthesiologist import MissingAnesthesiologistValidator
from validators.double_booking import DoubleBookingValidator

def main():
    print("=== AnesthesiaCopilot ===\n")

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")
    reader.read()

    builder = CaseBuilder(reader.workbook)

    cases = builder.build()
    print(cases[0])
    print(cases[0].end_time())

    print(f"\nFound {len(cases)} scheduled procedures\n")

    validator = MissingAnesthesiologistValidator()

    errors = validator.validate(cases)

    print(f"\nMissing anesthesiologist: {len(errors)}\n")

    for case in errors:
        print(case)

    double_booking = DoubleBookingValidator()
    double_booking.validate(cases)


if __name__ == "__main__":
    main()