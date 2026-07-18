import warnings

from app.incompatibility_reader import IncompatibilityReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService


class IncompatibilityService:

    def __init__(
        self,
        incompatibility_reader: IncompatibilityReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()
        self.incompatibilities = self._load_incompatibilities(
            incompatibility_reader
        )

    def has(self, anesthesiologist: str, surgeon: str) -> bool:

        if anesthesiologist is None or surgeon is None:
            return False

        identity = self.staff_identity_service.try_resolve(
            anesthesiologist
        )

        if not identity.resolved:
            return False

        return (identity.his_full_name, surgeon) in self.incompatibilities

    def _load_incompatibilities(
        self,
        incompatibility_reader: IncompatibilityReader,
    ):
        incompatibilities = set()

        for raw_name, surgeon in incompatibility_reader.read():
            identity = self.staff_identity_service.try_resolve(raw_name)

            if not identity.resolved:
                self._warn_unknown(raw_name)
                continue

            incompatibilities.add((identity.his_full_name, surgeon))

        return incompatibilities

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        warnings.warn(
            f"Unresolved staff identity from incompatibilities: "
            f"'{raw_name}'",
            stacklevel=2,
        )
