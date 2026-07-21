from datetime import date
import warnings

from app.models.patient_request import PatientRequest
from app.patient_requests_reader import PatientRequestsReader
from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService
from app.staff_warning import unresolved_staff_message


class PatientRequestService:

    def __init__(
        self,
        patient_requests_reader: PatientRequestsReader,
        staff_identity_service: StaffIdentityService,
    ):
        self.patient_requests_reader = patient_requests_reader
        self.staff_identity_service = staff_identity_service
        self._warned_unknowns = set()

    def get_requests_for_date(self, day: date) -> list[PatientRequest]:
        requests = self.patient_requests_reader.read(day)
        return self._resolve_requests(requests)

    def _resolve_requests(
        self,
        raw_requests: list[PatientRequest],
    ) -> list[PatientRequest]:
        canonical_requests = []

        for patient_request in raw_requests:
            identity = self.staff_identity_service.try_resolve(
                patient_request.requested_anesthesiologist
            )

            if not identity.resolved:
                self._warn_unknown(
                    patient_request.requested_anesthesiologist
                )
                continue

            canonical_requests.append(
                PatientRequest(
                    date=patient_request.date,
                    requested_anesthesiologist=identity.his_full_name,
                    patient=patient_request.patient,
                    surgeon=patient_request.surgeon,
                )
            )

        return canonical_requests

    def _warn_unknown(self, raw_name: str) -> None:
        warning_key = normalize_staff_name(raw_name)

        if warning_key in self._warned_unknowns:
            return

        self._warned_unknowns.add(warning_key)
        message = (
            f"Unresolved staff identity from Patient requests: "
            f"'{raw_name}'"
        )
        warnings.warn(
            unresolved_staff_message(
                message,
                raw_name,
                self.staff_identity_service,
            ),
            stacklevel=2,
        )
