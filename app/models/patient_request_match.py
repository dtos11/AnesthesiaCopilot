from dataclasses import dataclass

from app.models.case import Case
from app.models.patient_request import PatientRequest


@dataclass(frozen=True)
class PatientRequestMatch:
    request: PatientRequest
    case: Case
    confidence: float
