from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    UserRegisterSerializer, DoctorRegisterSerializer, HospitalRegisterSerializer,
    LoginSerializer, UserResponseSerializer, ChangePasswordSerializer,
)
from utils.auth_service import generate_tokens, authenticate_user, check_approval
from utils.response import success_response, error_response


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        user   = serializer.save()
        tokens = generate_tokens(user)
        return success_response(
            data={'tokens': tokens, 'user': UserResponseSerializer(user).data},
            message='Account created successfully.',
            status_code=201,
        )


class DoctorRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DoctorRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        user = serializer.save()
        return success_response(
            data={'user': UserResponseSerializer(user).data},
            message='Doctor registration submitted. Awaiting admin approval.',
            status_code=201,
        )


class HospitalRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = HospitalRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        user = serializer.save()
        return success_response(
            data={'user': UserResponseSerializer(user).data},
            message='Hospital registration submitted. Awaiting admin approval.',
            status_code=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)

        user = authenticate_user(
            serializer.validated_data['email'],
            serializer.validated_data['password'],
        )
        if not user:
            return error_response('Invalid email or password.', status_code=401)
        if not user.is_active:
            return error_response('Account deactivated.', status_code=403)

        allowed, reason = check_approval(user)
        if not allowed:
            return error_response(reason, status_code=403)

        tokens = generate_tokens(user)
        return success_response(
            data={'tokens': tokens, 'user': UserResponseSerializer(user).data},
            message='Login successful.',
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return error_response('Refresh token is required.')
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return error_response('Invalid or expired token.')
        return success_response(message='Logged out successfully.')


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserResponseSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return error_response('Old password is incorrect.')
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return success_response(message='Password changed successfully.')