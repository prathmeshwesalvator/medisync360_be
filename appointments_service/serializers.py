from rest_framework import serializers
from .models import Appointment, AppointmentReminder
import datetime


class AppointmentCreateSerializer(serializers.Serializer):
    # FIX: Flutter sends 'doctor' (int) and 'slot_id' (int)
    doctor  = serializers.IntegerField()
    slot_id = serializers.IntegerField()
    reason  = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        # FIX: correct import — was 'from medisync_360.doctors_service.models'
        # which resolves to package-level, causing ImportError at runtime
        from doctors_service.models import DoctorProfile, TimeSlot
        try:
            attrs['doctor_obj'] = DoctorProfile.objects.get(pk=attrs['doctor'])
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError({'doctor': 'Doctor not found.'})
        try:
            slot = TimeSlot.objects.get(pk=attrs['slot_id'], doctor=attrs['doctor_obj'])
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError({'slot_id': 'Slot not found.'})
        # FIX: use string literal — TimeSlot has no class-level AVAILABLE constant
        if slot.status != 'available':
            raise serializers.ValidationError({'slot_id': 'Slot is not available.'})
        if slot.date < datetime.date.today():
            raise serializers.ValidationError({'slot_id': 'Cannot book a past slot.'})
        attrs['slot'] = slot
        return attrs


class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name    = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email   = serializers.CharField(source='patient.email', read_only=True)
    patient_phone   = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name     = serializers.CharField(source='doctor.user.full_name', read_only=True)
    # FIX: Flutter reads 'doctor_specialty' — was serialized as 'specialization'
    doctor_specialty = serializers.CharField(source='doctor.specialization', read_only=True)
    hospital_name   = serializers.SerializerMethodField()
    # FIX: Flutter reads 'appointment_date' — model field is 'date'
    appointment_date = serializers.DateField(source='date', read_only=True)
    # FIX: Flutter reads 'slot_time' — model field is 'start_time'
    slot_time       = serializers.TimeField(source='start_time', read_only=True)
    # FIX: Flutter reads 'appointment_type' — not in model, derive from notes or default
    appointment_type = serializers.SerializerMethodField()

    class Meta:
        model  = Appointment
        fields = [
            'id', 'patient_name', 'patient_email', 'patient_phone',
            'doctor_name', 'doctor_specialty', 'hospital_name',
            'appointment_date', 'slot_time', 'appointment_type',
            'status', 'consultation_fee', 'payment_status',
            'reason', 'notes', 'cancel_reason', 'reschedule_count',
            'created_at', 'updated_at',
        ]

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

    def get_appointment_type(self, obj):
        # appointment_type is stored in notes prefix or defaults to in_person
        # If you add an appointment_type field to the model later, update here
        return getattr(obj, 'appointment_type', 'in_person')


class AppointmentDetailSerializer(AppointmentListSerializer):
    """Same as list — all fields already included above."""
    pass


class RescheduleSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()

    def validate_slot_id(self, value):
        # FIX: was 'from models import TimeSlot' — missing package path, crashes at runtime
        from doctors_service.models import TimeSlot
        try:
            slot = TimeSlot.objects.get(pk=value)
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError('Slot not found.')
        # FIX: use string literal
        if slot.status != 'available':
            raise serializers.ValidationError('Slot is not available.')
        if slot.date < datetime.date.today():
            raise serializers.ValidationError('Cannot reschedule to a past slot.')
        # Return the slot object so views.py can pass it directly to reschedule_appointment()
        return slot


class CancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')