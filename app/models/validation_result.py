from dataclasses import dataclass


@dataclass
class ValidationResult:
    name: str
    issues: list

    @property
    def passed(self):
        return len(self.issues) == 0

    @property
    def issue_count(self):
        return len(self.issues)