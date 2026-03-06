from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        APPOINTMENT_BOOKED     = 'appointment_booked',     'Appointment Booked'
        APPOINTMENT_CANCELLED  = 'appointment_cancelled',  'Appointment Cancelled'
        APPOINTMENT_REMINDER   = 'appointment_reminder',   'Appointment Reminder'
        APPOINTMENT_COMPLETED  = 'appointment_completed',  'Appointment Completed'
        APPOINTMENT_RESCHEDULED= 'appointment_rescheduled','Appointment Rescheduled'
        LAB_REPORT_UPLOADED    = 'lab_report_uploaded',    'Lab Report Uploaded'
        PRESCRIPTION_ADDED     = 'prescription_added',     'Prescription Added'
        GENERAL                = 'general',                'General'

    recipient   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=200)
    body        = models.TextField()
    notif_type  = models.CharField(max_length=50, choices=Type.choices, default=Type.GENERAL)
    data        = models.JSONField(default=dict, blank=True)   # extra payload for FCM
    is_read     = models.BooleanField(default=False)
    fcm_sent    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient} — {self.title}'


class FCMToken(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_tokens')
    token      = models.TextField(unique=True)
    device     = models.CharField(max_length=100, blank=True)  # 'android' | 'ios'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fcm_tokens'