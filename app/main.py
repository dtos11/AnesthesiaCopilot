from workbook_reader import WorkbookReader


def main():
    print("=== AnesthesiaCopilot ===\n")

    reader = WorkbookReader("sample_data/sample_schedule.xlsx")

    reader.read()
    reader.print_summary()


if __name__ == "__main__":
    main()