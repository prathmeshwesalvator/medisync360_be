from rest_framework import serializers
from .models import LabReport, ReportQuestion


class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = [
            'id', 'title', 'report_type', 'image', 'uploaded_at',
            'status', 'ocr_raw_text', 'extracted_data',
            'ai_analysis', 'ai_structured_result', 'notes'
        ]
        read_only_fields = [
            'uploaded_at', 'status', 'ocr_raw_text',
            'extracted_data', 'ai_analysis', 'ai_structured_result'
        ]


class LabReportUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = ['id', 'title', 'report_type', 'image', 'notes']


class LabReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = [
            'id', 'title', 'report_type', 'uploaded_at',
            'status', 'ai_structured_result'
        ]


class ReportQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportQuestion
        fields = ['id', 'question', 'answer', 'asked_at']
        read_only_fields = ['answer', 'asked_at']


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)