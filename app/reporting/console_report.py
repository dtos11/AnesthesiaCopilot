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

    def maternidad(self, previous_day, schedule_day) -> None:
        self.heading("MATERNIDAD")

        self.line("Post-call (previous day)")
        self.blank()
        self._obstetrics_assignments(previous_day)

        self.blank()

        self.line("On Call (schedule date)")
        self.blank()
        self._obstetrics_assignments(schedule_day)

        self.blank()

    def _obstetrics_assignments(self, assignments) -> None:
        if not assignments:
            self.line("    <none>")
            return

        for assignment in assignments:
            self.line(f"    {assignment.person}")

    def availability_overrides(self, overrides) -> None:
        self.heading("AVAILABILITY OVERRIDES")

        if not overrides:
            self.line("    None")
            self.blank()
            return

        for availability_override in overrides:
            self.line(availability_override.person)
            self.blank()

            for instruction in availability_override.instructions:
                self.line(f"    {instruction}")

            self.blank()

    def saturday_roster_calendar_integrity(self, result) -> None:
        self.heading("SATURDAY ROSTER CALENDAR INTEGRITY")

        if result.issue_count > 0:
            endoscopy_entries = result.issues[0]
            self.line(
                "ERROR: Expected exactly one E entry; "
                f"found {len(endoscopy_entries)}."
            )

        self.blank()

    def saturday_assignments_outside_roster(self, issues) -> None:
        self.heading("SATURDAY ASSIGNMENTS OUTSIDE ROSTER")

        if issues:
            self.line("WARNING: Additional Saturday staff require review.")
            self.blank()

        for person, cases in issues:
            area_counts = {}

            for case in cases:
                area_counts[case.area] = area_counts.get(case.area, 0) + 1

            areas = ", ".join(
                f"{area} ({count})"
                for area, count in area_counts.items()
            )
            self.line(person)
            self.line(f"    Cases : {len(cases)}")
            self.line(f"    Areas : {areas}")
            self.blank()

        self.blank()

    def endoscopy_assignment(self, issues) -> None:
        self.heading("ENDOSCOPY ASSIGNMENT")

        for issue in issues:
            self.line(f"ERROR: {issue}")

        self.blank()

    def patient_request_violations(self, violations) -> None:
        if not violations:
            return

        self.line("Patient requests violated")
        self.separator()

        for violation in violations:
            match = violation.match
            self.field("Patient", match.request.patient)
            self.field(
                "Requested",
                match.request.requested_anesthesiologist,
            )
            self.field(
                "Assigned",
                match.case.anesthesiologist or "<unassigned>",
            )
            self.field("Surgeon", match.request.surgeon)
            self.field("Area", match.case.area)
            self.field("Operating room", match.case.operating_room)
            self.field(
                "Scheduled time",
                match.case.scheduled_time.strftime("%H:%M"),
            )
            self.blank()

    def line(self, text: str = "") -> None:
        self._lines.append(text)

    def blank(self) -> None:
        self._lines.append("")

    def render(self) -> str:
        return "\n".join(self._lines)
