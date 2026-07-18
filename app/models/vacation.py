from datetime import date


class Vacation:

    def __init__(
        self,
        person: str,
        start: date,
        end: date,
        notation: str | None = None,
    ):
        self.person = person
        self.start = start
        self.end = end
        self.notation = notation

    def __str__(self):

        text = f"{self.person} ({self.start} - {self.end})"

        if self.notation:
            text += f" [{self.notation}]"

        return text

    def includes(self, day: date) -> bool:
        return self.start <= day < self.end
