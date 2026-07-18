from datetime import date


class Vacation:

    def __init__(
        self,
        person: str,
        start: date,
        end: date,
        replacement: str | None = None,
        needs_replacement: bool = False,
    ):
        self.person = person
        self.start = start
        self.end = end
        self.replacement = replacement
        self.needs_replacement = needs_replacement

    def __str__(self):

        text = f"{self.person} ({self.start} - {self.end})"

        if self.replacement:
            text += f" -> {self.replacement}"

        if self.needs_replacement:
            text += " [needs replacement]"

        return text

    def includes(self, day: date) -> bool:
        return self.start <= day < self.end
