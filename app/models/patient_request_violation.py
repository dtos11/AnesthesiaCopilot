from dataclasses import dataclass

from app.models.patient_request_match import PatientRequestMatch


@dataclass(frozen=True)
class PatientRequestViolation:
    match: PatientRequestMatch
