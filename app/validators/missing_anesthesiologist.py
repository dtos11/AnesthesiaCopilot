from validators.validator import Validator


class MissingAnesthesiologistValidator(Validator):

    def validate(self, cases):

        errors = []

        for case in cases:

            if (
                case.anesthesia_type != "ANESTESIA LOCAL"
                and case.anesthesiologist is None
            ):
                errors.append(case)

        return errors