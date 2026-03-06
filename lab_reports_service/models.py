from django.db import models
from django.conf import settings


class LabReport(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        PROCESSED = 'processed', 'Processed'
        VERIFIED  = 'verified',  'Verified'

    patient     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_reports')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_reports')
    doctor      = models.ForeignKey('doctors_service.DoctorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_reports')
    hospital    = models.ForeignKey('hospital_service.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_reports')
    appointment = models.ForeignKey('appointments_service.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_reports')

    title           = models.CharField(max_length=200)
    report_type     = models.CharField(max_length=100)     # e.g. "CBC", "LFT", "Blood Sugar"
    file_url        = models.URLField()
    test_date       = models.DateField()
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lab_reports'
        ordering = ['-test_date','-created_at']


class LabTestResult(models.Model):
    report      = models.ForeignKey(LabReport, on_delete=models.CASCADE, related_name='results')
    test_name   = models.CharField(max_length=200)
    value       = models.CharField(max_length=100)
    unit        = models.CharField(max_length=50, blank=True)
    normal_range= models.CharField(max_length=100, blank=True)
    is_abnormal = models.BooleanField(default=False)

    class Meta:
        db_table = 'lab_test_results'