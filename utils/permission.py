from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only users with role='admin'."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsDoctorRole(BasePermission):
    """Only users with role='doctor'."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'doctor'
        )


class IsHospitalRole(BasePermission):
    """Only users with role='hospital'."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'hospital'
        )


class IsHospitalOrAdmin(BasePermission):
    """Hospital users or admins."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['hospital', 'admin']
        )


class IsApproved(BasePermission):
    """User must have approval_status='approved' (for doctors/hospitals)."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.approval_status == 'approved'
        )