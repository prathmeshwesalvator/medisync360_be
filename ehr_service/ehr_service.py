from .models import MedicalHistory


def get_or_create_history(patient):
    obj, _ = MedicalHistory.objects.get_or_create(patient=patient)
    return obj


def can_access_ehr(requesting_user, patient_user) -> bool:
    """
    Access rules:
    - Patient can see own records.
    - Doctor can see if they have a confirmed/completed appointment with this patient.
    - Hospital can see if this patient has an appointment at their hospital.
    - Admin can see all.
    """
    if requesting_user == patient_user:
        return True
    if requesting_user.role == 'admin':
        return True
    if requesting_user.role == 'doctor':
        from appointments_service.models import Appointment
        return Appointment.objects.filter(
            doctor__user=requesting_user,
            patient=patient_user,
            status__in=['confirmed','completed','rescheduled'],
        ).exists()
    if requesting_user.role == 'hospital':
        from appointments_service.models import Appointment
        try:
            hospital = requesting_user.hospital
            return Appointment.objects.filter(hospital=hospital, patient=patient_user).exists()
        except Exception:
            return False
    return False