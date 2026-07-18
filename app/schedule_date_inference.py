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

FILENAME_PATTERN = re.compile(
    r"^\s*Lista\s+del\s+(?P<day>\d{1,2})\s+de\s+"
    r"(?P<month>[A-Za-z]+)\.xlsx\s*$",
    re.IGNORECASE,
)


def infer_schedule_date(
    workbook_path: str,
    today: date | None = None,
) -> date:
    filename = Path(workbook_path).name
    match = FILENAME_PATTERN.fullmatch(filename)

    if match is None:
        raise ValueError(
            "Cannot infer schedule date from filename "
            f"'{filename}'. Expected 'Lista del <day> de <Spanish month>.xlsx'."
        )

    month_name = match.group("month").casefold()
    month = SPANISH_MONTHS.get(month_name)

    if month is None:
        raise ValueError(
            f"Cannot infer schedule date from filename '{filename}': "
            f"unknown Spanish month '{match.group('month')}'."
        )

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
