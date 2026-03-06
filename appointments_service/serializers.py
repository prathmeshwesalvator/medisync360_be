from rest_framework import serializers
from .models import Appointment, AppointmentReminder
from doctors_service.serializers import DoctorListSerializer
import datetime


class AppointmentCreateSerializer(serializers.Serializer):
    doctor_id  = serializers.IntegerField()
    slot_id    = serializers.IntegerField()
    reason     = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        from medisync_360.doctors_service.models import DoctorProfile, TimeSlot
        try:
            attrs['doctor'] = DoctorProfile.objects.get(pk=attrs['doctor_id'])
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Doctor not found.'})
        try:
            slot = TimeSlot.objects.get(pk=attrs['slot_id'], doctor=attrs['doctor'])
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError({'slot_id': 'Slot not found.'})
        if slot.status != TimeSlot.AVAILABLE:
            raise serializers.ValidationError({'slot_id': 'Slot is not available.'})
        if slot.date < datetime.date.today():
            raise serializers.ValidationError({'slot_id': 'Cannot book a past slot.'})
        attrs['slot'] = slot
        return attrs


class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name  = serializers.CharField(source='doctor.user.full_name', read_only=True)
    specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    hospital_name  = serializers.SerializerMethodField()
    class Meta:
        model  = Appointment
        fields = ['id','patient_name','doctor_name','specialization','hospital_name',
                  'date','start_time','end_time','status','consultation_fee',
                  'payment_status','reason','created_at']
    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None


class AppointmentDetailSerializer(AppointmentListSerializer):
    class Meta(AppointmentListSerializer.Meta):
        fields = AppointmentListSerializer.Meta.fields + ['notes','cancel_reason','reschedule_count','updated_at']


class RescheduleSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()
    def validate_slot_id(self, value):
        from models import TimeSlot
        try:
            slot = TimeSlot.objects.get(pk=value)
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError('Slot not found.')
        if slot.status != TimeSlot.AVAILABLE:
            raise serializers.ValidationError('Slot is not available.')
        if slot.date < datetime.date.today():
            raise serializers.ValidationError('Cannot reschedule to a past slot.')
        return slot


class CancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)