from rapidfuzz import fuzz

from app.models.case import Case
from app.models.patient_request import PatientRequest
from app.models.patient_request_match import PatientRequestMatch


PATIENT_MATCH_THRESHOLD = 85.0


class PatientRequestMatcher:

    def match(
        self,
        requests: list[PatientRequest],
        cases: list[Case],
    ) -> list[PatientRequestMatch]:
        matches = []

        for patient_request in requests:
            candidate_cases = [
                case
                for case in cases
                if case.date == patient_request.date
                and self._surgeon_surname(case.surgeon)
                == patient_request.surgeon.strip().casefold()
            ]
            scored_candidates = [
                (
                    case,
                    fuzz.ratio(
                        self._patient_surname(patient_request.patient),
                        self._patient_surname(case.patient),
                    ),
                )
                for case in candidate_cases
            ]

            if not scored_candidates:
                continue

            best_score = max(
                score
                for _, score in scored_candidates
            )

            if best_score < PATIENT_MATCH_THRESHOLD:
                continue

            best_cases = [
                case
                for case, score in scored_candidates
                if score == best_score
            ]

            if len(best_cases) != 1:
                continue

            matches.append(
                PatientRequestMatch(
                    request=patient_request,
                    case=best_cases[0],
                    confidence=best_score,
                )
            )

        return matches

    @staticmethod
    def _surgeon_surname(surgeon: str) -> str:
        return surgeon.strip().split(maxsplit=1)[0].casefold()

    @staticmethod
    def _patient_surname(patient: str) -> str:
        return patient.strip().split(maxsplit=1)[0].casefold()
