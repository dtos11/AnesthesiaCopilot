from app.privilege_reader import PrivilegeReader


class PrivilegeService:

    def __init__(self, privilege_reader: PrivilegeReader):
        self.privileges = privilege_reader.read()

    def has(self, person: str, privilege: str) -> bool:

        if person is None:
            return False

        return person in self.privileges.get(privilege, set())