from rest_framework import serializers
from .models import DoctorProfile, WeeklySchedule, SlotBlock, TimeSlot, DoctorReview

class WeeklyScheduleSerializer(serializers.ModelSerializer):
    day_label = serializers.CharField(source='get_day_of_week_display', read_only=True)
    class Meta:
        model  = WeeklySchedule
        fields = ['id','day_of_week','day_label','start_time','end_time',
                  'slot_duration_minutes','max_patients','is_active']

class SlotBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SlotBlock
        fields = ['id','date','reason']

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TimeSlot
        fields = ['id','date','start_time','end_time','status']

class DoctorListSerializer(serializers.ModelSerializer):
    full_name            = serializers.CharField(source='user.full_name', read_only=True)
    email                = serializers.CharField(source='user.email', read_only=True)
    phone                = serializers.CharField(source='user.phone', read_only=True)
    specialization_label = serializers.CharField(source='get_specialization_display', read_only=True)
    hospital_name        = serializers.SerializerMethodField()
    class Meta:
        model  = DoctorProfile
        fields = ['id','full_name','email','phone','specialization','specialization_label',
                  'qualification','experience_years','consultation_fee','rating',
                  'total_reviews','is_available_today','hospital_name','languages']
    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

class DoctorDetailSerializer(serializers.ModelSerializer):
    full_name            = serializers.CharField(source='user.full_name', read_only=True)
    email                = serializers.CharField(source='user.email', read_only=True)
    phone                = serializers.CharField(source='user.phone', read_only=True)
    specialization_label = serializers.CharField(source='get_specialization_display', read_only=True)
    weekly_schedule      = WeeklyScheduleSerializer(many=True, read_only=True)
    hospital_name        = serializers.SerializerMethodField()
    class Meta:
        model  = DoctorProfile
        fields = ['id','full_name','email','phone','specialization','specialization_label',
                  'qualification','experience_years','license_number','bio','languages',
                  'consultation_fee','rating','total_reviews','is_available_today',
                  'weekly_schedule','hospital_name','created_at']
    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

class DoctorProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model   = DoctorProfile
        exclude = ['user','rating','total_reviews','created_at','updated_at']

class DoctorReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    class Meta:
        model  = DoctorReview
        fields = ['id','rating','comment','patient_name','created_at']