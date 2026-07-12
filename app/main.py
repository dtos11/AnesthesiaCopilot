from workbook_reader import WorkbookReader
from case_builder import CaseBuilder


def main():
    print("=== AnesthesiaCopilot ===\n")

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")
    reader.read()

    builder = CaseBuilder(reader.workbook)

    cases = builder.build()

    print(f"\nFound {len(cases)} scheduled procedures\n")

    for case in cases[:10]:
        print(case)


if __name__ == "__main__":
    main()