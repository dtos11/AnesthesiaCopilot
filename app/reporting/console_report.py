class ConsoleReport:
    WIDTH = 57

    def __init__(self):
        self._lines: list[str] = []

    def title(self, text: str) -> None:
        self._lines.append("=" * self.WIDTH)
        self._lines.append(text)
        self._lines.append("=" * self.WIDTH)
        self.blank()

    def heading(self, text: str) -> None:
        self.separator()
        self._lines.append(text)
        self.separator()
        self.blank()

    def separator(self) -> None:
        self._lines.append("-" * self.WIDTH)

    def field(self, key: str, value) -> None:
        self._lines.append(f"{key:<28}: {value}")

    def guardias(self, previous_day, schedule_day) -> None:
        self.heading("GUARDIAS")

        self.line("Post-call (previous day)")
        self.blank()
        self._call_assignment("First", previous_day, role=1)
        self._call_assignment("Second", previous_day, role=2)

        self.blank()

        self.line("On Call (schedule date)")
        self.blank()
        self._call_assignment("First", schedule_day, role=1)
        self._call_assignment("Second", schedule_day, role=2)

        self.blank()

    def _call_assignment(self, label, assignments, role: int) -> None:
        names = [
            assignment.person
            for assignment in assignments
            if assignment.role == role
        ]

        value = ", ".join(names) if names else "<missing>"
        self.line(f"    {label:<7}: {value}")

    def line(self, text: str = "") -> None:
        self._lines.append(text)

    def blank(self) -> None:
        self._lines.append("")

    def render(self) -> str:
        return "\n".join(self._lines)
