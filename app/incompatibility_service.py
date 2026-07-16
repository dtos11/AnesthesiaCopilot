from app.incompatibility_reader import IncompatibilityReader


class IncompatibilityService:

    def __init__(self, incompatibility_reader: IncompatibilityReader):
        self.incompatibilities = incompatibility_reader.read()

    def has(self, anesthesiologist: str, surgeon: str) -> bool:

        if anesthesiologist is None or surgeon is None:
            return False

        return (
            anesthesiologist,
            surgeon,
        ) in self.incompatibilities