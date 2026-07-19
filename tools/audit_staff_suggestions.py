"""Manually audit staff-identity suggestions against representative inputs.

Run from the repository root with:

    .venv/bin/python tools/audit_staff_suggestions.py

Use this utility whenever staff members are added, aliases change, the matching
algorithm changes, or the similarity threshold changes.
"""

from dataclasses import dataclass
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.staff_directory_reader import StaffDirectoryReader  # noqa: E402
from app.staff_identity_service import StaffIdentityService  # noqa: E402


@dataclass(frozen=True)
class AuditCase:
    raw_name: str
    expected_canonical_name: str | None


AUDIT_CASES = (
    AuditCase("GRIMBALTT", "Grimblatt Gustavo"),
    AuditCase("GRIMBLAT", "Grimblatt Gustavo"),
    AuditCase("BETULARR", "Betular Haas Juan Ignacio"),
    AuditCase("BETULARR", "Betular Haas Juan Ignacio"),
    AuditCase("MEGA DIAZZ", "Mega Diaz Federico Andres"),
    AuditCase("MEGADIAZ", "Mega Diaz Federico Andres"),
    AuditCase("MEGA DIZ", "Mega Diaz Federico Andres"),
    AuditCase("HWANGG", "Hwang In Hyuk"),
    AuditCase("DIEGO HWANG", "Hwang In Hyuk"),
    AuditCase("SZMULEWIZ", "Szmulewicz Hernan Ezequiel"),
    AuditCase("SZMULEWIC", "Szmulewicz Hernan Ezequiel"),
    AuditCase("GARASSA", "Garasa Maximiliano Ricardo"),
    AuditCase("NOZIER", "Nozieres Christian"),
    AuditCase("SANCHEZ CROCCI", "Sanchez Crocci Fermin"),
    AuditCase("FERMIN SANCHEZ", "Sanchez Crocci Fermin"),
    AuditCase("LAFUENTE", "Lafuente Esteban Jose"),
    AuditCase("VELLOSSO", "Veloso Alberto"),
    AuditCase("COSTALLES", "Costales Alfredo Jose"),
    AuditCase("BASSO/MONTANARO", None),
    AuditCase("ALERGIA AL LATEX", None),
    AuditCase("CONGRESO ANESTESIOLOGIA", None),
    AuditCase("PEDIDO", None),
    AuditCase("1/2", None),
)


def main() -> None:
    identity_service = StaffIdentityService(
        StaffDirectoryReader(
            REPOSITORY_ROOT / "sample_data/department_staff.xlsx"
        )
    )
    missed_typos = []
    competing_suggestions = []
    possible_false_positives = []

    print(
        "Staff suggestion audit "
        f"(cutoff={identity_service.SUGGESTION_SCORE_CUTOFF:.1f})"
    )
    print()

    for audit_case in AUDIT_CASES:
        resolution = identity_service.try_resolve(audit_case.raw_name)
        suggestions = identity_service.suggest(audit_case.raw_name)

        print(f"Input       : {audit_case.raw_name}")
        print(
            "Resolved    : "
            + (resolution.his_full_name if resolution.resolved else "<no>")
        )

        if suggestions:
            print("Suggestions :")
            for suggestion in suggestions:
                print(
                    f"    {suggestion.canonical_name} "
                    f"({suggestion.similarity_score:.2f})"
                )
        else:
            print("Suggestions : <none>")

        print()

        observed_names = {
            suggestion.canonical_name
            for suggestion in suggestions
        }
        if resolution.resolved:
            observed_names.add(resolution.his_full_name)

        expected = audit_case.expected_canonical_name

        if expected is not None and expected not in observed_names:
            missed_typos.append(audit_case.raw_name)

        if len(suggestions) > 1:
            competing_suggestions.append(audit_case.raw_name)

        if expected is None and suggestions:
            possible_false_positives.append(audit_case.raw_name)
        elif expected is not None and suggestions:
            if suggestions[0].canonical_name != expected:
                possible_false_positives.append(audit_case.raw_name)

    print("SUMMARY")
    print("-------")
    print_items("Missed obvious typos", missed_typos)
    print_items("Multiple competing suggestions", competing_suggestions)
    print_items("Possible false positives", possible_false_positives)


def print_items(label: str, values: list[str]) -> None:
    display = ", ".join(values) if values else "<none>"
    print(f"{label}: {display}")


if __name__ == "__main__":
    main()
