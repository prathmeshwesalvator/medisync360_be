from rest_framework import serializers
from .models import MedicalHistory, Prescription, Medicine, DoctorNote, ImagingRecord

class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model   = MedicalHistory
        exclude = ['patient']

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Medicine
        exclude = ['prescription']

class PrescriptionSerializer(serializers.ModelSerializer):
    medicines   = MedicineSerializer(many=True, read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    class Meta:
        model  = Prescription
        fields = ['id','appointment','doctor_name','diagnosis','notes','follow_up_date','medicines','created_at']

class PrescriptionWriteSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True)
    class Meta:
        model   = Prescription
        exclude = ['patient','doctor','created_at','updated_at']

    def create(self, validated_data):
        meds_data = validated_data.pop('medicines', [])
        prescription = Prescription.objects.create(**validated_data)
        for m in meds_data:
            Medicine.objects.create(prescription=prescription, **m)
        return prescription

class DoctorNoteSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    class Meta:
        model  = DoctorNote
        fields = ['id','appointment','doctor_name','note','is_private','created_at']

class ImagingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ImagingRecord
        fields = ['id','imaging_type','body_part','file_url','findings','date_taken','created_at']