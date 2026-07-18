from dataclasses import dataclass

from app.staff_directory_reader import (
    StaffDirectoryReader,
    normalize_staff_name,
)


class UnknownStaffIdentityError(LookupError):

    def __init__(self, raw_name: str):
        self.raw_name = raw_name
        super().__init__(f"Unknown staff identity: '{raw_name}'")


@dataclass(frozen=True)
class StaffIdentityResolution:
    raw_name: str
    his_full_name: str | None

    @property
    def resolved(self) -> bool:
        return self.his_full_name is not None


class StaffIdentityService:

    def __init__(self, directory_reader: StaffDirectoryReader):
        staff, aliases = directory_reader.read()
        self._identity_by_key = {
            normalize_staff_name(record.his_full_name): record.his_full_name
            for record in staff
        }

        for alias in aliases:
            self._identity_by_key[
                normalize_staff_name(alias.alias)
            ] = alias.his_full_name

    def resolve(self, raw_name: str) -> str:
        resolution = self.try_resolve(raw_name)

        if not resolution.resolved:
            raise UnknownStaffIdentityError(raw_name)

        return resolution.his_full_name

    def try_resolve(self, raw_name: str) -> StaffIdentityResolution:
        if not isinstance(raw_name, str) or not raw_name.strip():
            return StaffIdentityResolution(
                raw_name=raw_name,
                his_full_name=None,
            )

        return StaffIdentityResolution(
            raw_name=raw_name,
            his_full_name=self._identity_by_key.get(
                normalize_staff_name(raw_name)
            ),
        )

    def same_person(self, left_name: str, right_name: str) -> bool:
        return self.resolve(left_name) == self.resolve(right_name)
