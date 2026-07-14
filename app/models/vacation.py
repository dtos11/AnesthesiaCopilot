from datetime import date


class Vacation:

    def __init__(
        self,
        person: str,
        start: date,
        end: date,
        replacement: str | None = None,
    ):
        self.person = person
        self.start = start
        self.end = end
        self.replacement = replacement

    def __str__(self):
        if self.replacement:
            return (
                f"{self.person} "
                f"({self.start} - {self.end}) "
                f"-> {self.replacement}"
            )

        return f"{self.person} ({self.start} - {self.end})"