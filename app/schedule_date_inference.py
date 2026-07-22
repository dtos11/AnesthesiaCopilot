import re
from datetime import date
from pathlib import Path


SPANISH_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

DATE_PATTERN = re.compile(
    r"(?<!\d)(?P<day>\d{1,2})\s+(?:de\s+)?"
    rf"(?P<month>{'|'.join(SPANISH_MONTHS)})\b",
    re.IGNORECASE,
)
XLSX_PATTERN = re.compile(r"\.xlsx\s*$", re.IGNORECASE)


def infer_schedule_date(
    workbook_path: str,
    today: date | None = None,
) -> date:
    filename = Path(workbook_path).name
    extension_match = XLSX_PATTERN.search(filename)
    matches = (
        list(DATE_PATTERN.finditer(filename[:extension_match.start()]))
        if extension_match is not None
        else []
    )

    if len(matches) != 1:
        raise ValueError(
            "Cannot infer schedule date from filename "
            f"'{filename}'. Expected one unambiguous day and "
            "Spanish month in an .xlsx filename."
        )

    match = matches[0]
    month_name = match.group("month").casefold()
    month = SPANISH_MONTHS[month_name]

    day = int(match.group("day"))
    reference_date = today or date.today()
    candidate_years = (
        reference_date.year,
        reference_date.year - 1,
        reference_date.year + 1,
    )

    candidates = []

    for year in candidate_years:
        try:
            candidates.append(date(year, month, day))
        except ValueError:
            continue

    if not candidates:
        raise ValueError(
            f"Cannot infer schedule date from filename '{filename}': "
            f"invalid day {day} for {match.group('month')}."
        )

    return min(
        candidates,
        key=lambda candidate: abs(candidate - reference_date),
    )
