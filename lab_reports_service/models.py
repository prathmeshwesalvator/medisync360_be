from django.db import models
from django.conf import settings


class LabReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('blood_test', 'Blood Test'),
        ('urine_test', 'Urine Test'),
        ('lipid_panel', 'Lipid Panel'),
        ('liver_function', 'Liver Function Test'),
        ('kidney_function', 'Kidney Function Test'),
        ('thyroid', 'Thyroid Panel'),
        ('cbc', 'Complete Blood Count'),
        ('diabetes', 'Diabetes Panel'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_reports'
    )
    title = models.CharField(max_length=255, blank=True)
    report_type = models.CharField(
        max_length=50, choices=REPORT_TYPE_CHOICES, default='other'
    )
    image = models.ImageField(upload_to="lab_reports/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # OCR extracted raw text
    ocr_raw_text = models.TextField(blank=True, null=True)

    # Structured data extracted from OCR
    extracted_data = models.JSONField(blank=True, null=True)

    # GPT analysis result
    ai_analysis = models.TextField(blank=True, null=True)

    # Structured GPT output stored as JSON
    ai_structured_result = models.JSONField(blank=True, null=True)

    # Patient notes
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user} - {self.report_type} - {self.uploaded_at.date()}"


class ReportQuestion(models.Model):
    """Stores follow-up questions asked by user about a specific report."""
    report = models.ForeignKey(
        LabReport, on_delete=models.CASCADE, related_name='questions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['asked_at']

    def __str__(self):
        return f"Q: {self.question[:60]}..."