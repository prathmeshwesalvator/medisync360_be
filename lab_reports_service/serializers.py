from rest_framework import serializers
from .models import LabReport, LabTestResult

class LabTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LabTestResult
        exclude = ['report']

class LabReportSerializer(serializers.ModelSerializer):
    results         = LabTestResultSerializer(many=True, read_only=True)
    uploaded_by_name= serializers.CharField(source='uploaded_by.full_name', read_only=True)
    patient_name    = serializers.CharField(source='patient.full_name', read_only=True)
    class Meta:
        model  = LabReport
        fields = ['id','patient_name','uploaded_by_name','title','report_type',
                  'file_url','test_date','status','notes','results','created_at']

class LabReportCreateSerializer(serializers.ModelSerializer):
    results = LabTestResultSerializer(many=True, required=False)
    class Meta:
        model   = LabReport
        exclude = ['patient','uploaded_by','doctor','hospital','created_at','updated_at']

    def create(self, validated_data):
        results_data = validated_data.pop('results', [])
        report = LabReport.objects.create(**validated_data)
        for r in results_data:
            LabTestResult.objects.create(report=report, **r)
        return report