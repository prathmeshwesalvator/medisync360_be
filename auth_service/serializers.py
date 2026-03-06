from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from doctors_service.models import DoctorProfile
from auth_service.models import User
from hospital_service.models import Hospital as HospitalProfile


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DoctorProfile
        exclude = ['user', 'created_at']


class HospitalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HospitalProfile
        exclude = ['user', 'created_at']


# ── Register ──────────────────────────────────────────────────────────────────

class UserRegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        # validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(role=User.Role.USER, **validated_data)


class DoctorRegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    doctor_profile   = DoctorProfileSerializer()

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password', 'confirm_password', 'doctor_profile']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        # validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('doctor_profile')
        user = User.objects.create_user(role=User.Role.DOCTOR, **validated_data)
        DoctorProfile.objects.create(user=user, **profile_data)
        return user


class HospitalRegisterSerializer(serializers.ModelSerializer):
    password          = serializers.CharField(write_only=True, min_length=8)
    confirm_password  = serializers.CharField(write_only=True)
    hospital_profile  = HospitalProfileSerializer()

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password', 'confirm_password', 'hospital_profile']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        # validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('hospital_profile')
        user = User.objects.create_user(role=User.Role.HOSPITAL, **validated_data)
        HospitalProfile.objects.create(user=user, **profile_data)
        return user


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField()


# ── Response ──────────────────────────────────────────────────────────────────

class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'role',
            'approval_status', 'profile_picture',
            'date_joined',
        ]


# ── Change Password ───────────────────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password          = serializers.CharField()
    new_password          = serializers.CharField(min_length=8)
    confirm_new_password  = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'Passwords do not match.'})
        validate_password(attrs['new_password'])
        return attrs