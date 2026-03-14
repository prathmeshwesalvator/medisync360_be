from django.contrib import admin
from .models import LabReport, ReportQuestion


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'report_type', 'status', 'uploaded_at']
    list_filter = ['status', 'report_type']
    search_fields = ['user__email', 'report_type']
    readonly_fields = ['ocr_raw_text', 'extracted_data', 'ai_analysis', 'ai_structured_result', 'uploaded_at']


@admin.register(ReportQuestion)
class ReportQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'report', 'asked_at']
    readonly_fields = ['answer', 'asked_at']