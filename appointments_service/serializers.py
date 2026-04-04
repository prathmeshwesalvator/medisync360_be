from rest_framework import serializers
from .models import Appointment, AppointmentStatusLog, AppointmentReminder
import datetime


# ── Status log ────────────────────────────────────────────────────────────────

class AppointmentStatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = AppointmentStatusLog
        fields = ['id', 'from_status', 'to_status', 'changed_by_name', 'reason', 'changed_at']

    def get_changed_by_name(self, obj):
        return obj.changed_by.full_name if obj.changed_by else None


# ── Create ────────────────────────────────────────────────────────────────────

class AppointmentCreateSerializer(serializers.Serializer):
    doctor           = serializers.IntegerField()
    slot_id          = serializers.IntegerField()
    reason           = serializers.CharField(required=False, allow_blank=True, default='')
    symptoms         = serializers.CharField(required=False, allow_blank=True, default='')
    appointment_type = serializers.ChoiceField(
        choices=Appointment.AppointmentType.choices,
        default=Appointment.AppointmentType.IN_PERSON,
    )

    def validate(self, attrs):
        from doctors_service.models import DoctorProfile, TimeSlot
        try:
            attrs['doctor_obj'] = DoctorProfile.objects.get(pk=attrs['doctor'])
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError({'doctor': 'Doctor not found.'})
        try:
            slot = TimeSlot.objects.get(pk=attrs['slot_id'], doctor=attrs['doctor_obj'])
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError({'slot_id': 'Slot not found.'})
        if slot.status != 'available':
            raise serializers.ValidationError({'slot_id': 'Slot is not available.'})
        if slot.date < datetime.date.today():
            raise serializers.ValidationError({'slot_id': 'Cannot book a past slot.'})
        attrs['slot'] = slot
        return attrs


# ── List & Detail ─────────────────────────────────────────────────────────────

class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name     = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email    = serializers.CharField(source='patient.email', read_only=True)
    patient_phone    = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name      = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_specialty = serializers.CharField(source='doctor.specialization', read_only=True)
    hospital_name    = serializers.SerializerMethodField()
    appointment_date = serializers.DateField(source='date', read_only=True)
    slot_time        = serializers.TimeField(source='start_time', read_only=True)
    status_logs      = AppointmentStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model  = Appointment
        fields = [
            'id',
            'patient_name', 'patient_email', 'patient_phone',
            'doctor_name', 'doctor_specialty', 'hospital_name',
            'appointment_date', 'slot_time', 'appointment_type',
            'status', 'consultation_fee', 'payment_status',
            'reason', 'symptoms', 'notes', 'diagnosis', 'prescription',
            'cancel_reason', 'reschedule_count',
            'confirmed_at', 'completed_at', 'meeting_link',
            'payment_marked_at',
            'created_at', 'updated_at',
            'status_logs',
        ]

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None


class AppointmentDetailSerializer(AppointmentListSerializer):
    """Identical to list — all fields already present."""
    pass


# ── Doctor actions ────────────────────────────────────────────────────────────

class ConfirmAppointmentSerializer(serializers.Serializer):
    meeting_link = serializers.URLField(required=False, allow_blank=True, default='')


class CompleteAppointmentSerializer(serializers.Serializer):
    notes        = serializers.CharField(required=False, allow_blank=True, default='')
    diagnosis    = serializers.CharField(required=False, allow_blank=True, default='')
    prescription = serializers.CharField(required=False, allow_blank=True, default='')


class UpdateNotesSerializer(serializers.Serializer):
    notes        = serializers.CharField(required=False, allow_blank=True, default='')
    diagnosis    = serializers.CharField(required=False, allow_blank=True, default='')
    prescription = serializers.CharField(required=False, allow_blank=True, default='')


# ── Patient actions ───────────────────────────────────────────────────────────

class RescheduleSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()

    def validate_slot_id(self, value):
        from doctors_service.models import TimeSlot
        try:
            slot = TimeSlot.objects.get(pk=value)
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError('Slot not found.')
        if slot.status != 'available':
            raise serializers.ValidationError('Slot is not available.')
        if slot.date < datetime.date.today():
            raise serializers.ValidationError('Cannot reschedule to a past slot.')
        return slot


class CancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')