from django.db import models
from django.conf import settings


class MedicalHistory(models.Model):
    patient      = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_history')
    blood_group  = models.CharField(max_length=10, blank=True)
    allergies    = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications= models.TextField(blank=True)
    past_surgeries     = models.TextField(blank=True)
    family_history     = models.TextField(blank=True)
    emergency_contact_name  = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_history'


class Prescription(models.Model):
    appointment = models.OneToOneField('appointments_service.Appointment', on_delete=models.CASCADE, related_name='prescription', null=True, blank=True)
    patient     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    doctor      = models.ForeignKey('doctors_service.DoctorProfile', on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis   = models.TextField()
    notes       = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']


class Medicine(models.Model):
    FREQ = [('once','Once daily'),('twice','Twice daily'),('thrice','Three times daily'),('sos','SOS'),('other','Other')]
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    name         = models.CharField(max_length=200)
    dosage       = models.CharField(max_length=100)
    frequency    = models.CharField(max_length=20, choices=FREQ)
    duration_days= models.PositiveIntegerField(default=0)
    instructions = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'prescription_medicines'


class DoctorNote(models.Model):
    appointment = models.OneToOneField('appointments_service.Appointment', on_delete=models.CASCADE, related_name='doctor_note', null=True, blank=True)
    patient     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_notes')
    doctor      = models.ForeignKey('doctors_service.DoctorProfile', on_delete=models.CASCADE, related_name='doctor_notes')
    note        = models.TextField()
    is_private  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctor_notes'
        ordering = ['-created_at']


class ImagingRecord(models.Model):
    TYPE = [('xray','X-Ray'),('mri','MRI'),('ct','CT Scan'),('ultrasound','Ultrasound'),('other','Other')]
    patient      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='imaging_records')
    doctor       = models.ForeignKey('doctors_service.DoctorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='imaging_records')
    hospital     = models.ForeignKey('hospital_service.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='imaging_records')
    imaging_type = models.CharField(max_length=20, choices=TYPE)
    body_part    = models.CharField(max_length=100)
    file_url     = models.URLField()
    findings     = models.TextField(blank=True)
    date_taken   = models.DateField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imaging_records'
        ordering = ['-date_taken']