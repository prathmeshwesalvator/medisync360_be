from django.contrib.auth import authenticate
from auth_service.models import User
from rest_framework_simplejwt.tokens import RefreshToken



def generate_tokens(user: User) -> dict:
    """Generate JWT access + refresh token pair, embed role in payload."""
    refresh = RefreshToken.for_user(user)
    refresh['role']      = user.role
    refresh['full_name'] = user.full_name
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


def authenticate_user(email: str, password: str):
    return authenticate(username=email, password=password)


def check_approval(user: User) -> tuple:
    """Returns (is_allowed: bool, reason: str)."""
    if user.role in [User.Role.DOCTOR, User.Role.HOSPITAL]:
        if user.approval_status == User.ApprovalStatus.PENDING:
            return False, 'Your account is pending admin approval.'
        if user.approval_status == User.ApprovalStatus.REJECTED:
            return False, 'Your account has been rejected. Please contact support.'
    return True, ''