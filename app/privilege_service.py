import warnings

from app.privilege_reader import PrivilegeReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService


class PrivilegeService:

    def __init__(
        self,
        privilege_reader: PrivilegeReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()
        self.privileges = self._load_privileges(privilege_reader)

    def has(self, person: str, privilege: str) -> bool:

        if person is None:
            return False

        if privilege not in self.privileges:

            available = ", ".join(sorted(self.privileges.keys()))

            raise ValueError(
                f"Unknown privilege '{privilege}'. "
                f"Available privileges: {available}"
            )

        identity = self.staff_identity_service.try_resolve(person)

        if not identity.resolved:
            return False

        return identity.his_full_name in self.privileges[privilege]

    def _load_privileges(self, privilege_reader: PrivilegeReader):
        canonical_privileges = {}

        for privilege, raw_people in privilege_reader.read().items():
            canonical_people = set()

            for raw_name in raw_people:
                identity = self.staff_identity_service.try_resolve(
                    raw_name
                )

                if not identity.resolved:
                    self._warn_unknown(raw_name)
                    continue

                canonical_people.add(identity.his_full_name)

            canonical_privileges[privilege] = canonical_people

        return canonical_privileges

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        warnings.warn(
            f"Unresolved staff identity from privileges: '{raw_name}'",
            stacklevel=2,
        )
