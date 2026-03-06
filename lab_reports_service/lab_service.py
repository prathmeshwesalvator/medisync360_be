from .models import LabReport


def can_access_report(requesting_user, report: LabReport) -> bool:
    if requesting_user.role == 'admin':
        return True
    if report.patient == requesting_user:
        return True
    if requesting_user.role == 'doctor' and report.doctor and report.doctor.user == requesting_user:
        return True
    if requesting_user.role == 'hospital' and report.hospital:
        try:
            return report.hospital.user == requesting_user
        except Exception:
            return False
    return False