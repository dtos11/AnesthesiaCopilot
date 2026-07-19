import re

from app.staff_identity_service import (
    StaffIdentityService,
    StaffSuggestion,
)


SCHEDULE_NOTATION_PATTERN = re.compile(r"\s+[12]/2\s*$")


def unresolved_staff_message(
    message: str,
    raw_name: str,
    identity_service: StaffIdentityService,
) -> str:
    suggestions = identity_service.suggest(raw_name)

    if not suggestions:
        name_without_notation = SCHEDULE_NOTATION_PATTERN.sub(
            "",
            str(raw_name),
        )

        if name_without_notation != raw_name:
            suggestions = identity_service.suggest(
                name_without_notation
            )

    if not suggestions:
        return message

    return "\n".join(
        [message, "Did you mean:"]
        + [
            _suggestion_line(suggestion)
            for suggestion in sorted(
                suggestions,
                key=lambda item: item.similarity_score,
                reverse=True,
            )
        ]
    )


def _suggestion_line(suggestion: StaffSuggestion) -> str:
    return (
        f"    • {suggestion.canonical_name} "
        f"({suggestion.similarity_score:.1f}%)"
    )
