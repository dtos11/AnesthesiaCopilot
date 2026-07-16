from app.privilege_reader import PrivilegeReader


class PrivilegeService:

    def __init__(self, privilege_reader: PrivilegeReader):
        self.privileges = privilege_reader.read()

    def has(self, person: str, privilege: str) -> bool:

        if person is None:
            return False

        if privilege not in self.privileges:

            available = ", ".join(sorted(self.privileges.keys()))

            raise ValueError(
                f"Unknown privilege '{privilege}'. "
                f"Available privileges: {available}"
            )

        return person in self.privileges[privilege]