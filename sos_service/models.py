from django.db import models
from django.conf import settings


class SOSAlert(models.Model):
    class Status(models.TextChoices):
        ACTIVE    = 'active',    'Active'        # patient fired SOS, waiting for hospital
        ACCEPTED  = 'accepted',  'Accepted'      # a hospital confirmed they're coming
        ENROUTE   = 'enroute',   'En Route'      # ambulance dispatched
        ARRIVED   = 'arrived',   'Arrived'       # ambulance reached patient
        RESOLVED  = 'resolved',  'Resolved'      # case closed
        CANCELLED = 'cancelled', 'Cancelled'     # patient cancelled

    class Severity(models.TextChoices):
        CRITICAL  = 'critical',  'Critical'
        HIGH      = 'high',      'High'
        MEDIUM    = 'medium',    'Medium'

    patient         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sos_alerts',
        limit_choices_to={'role': 'user'},
    )
    responding_hospital = models.ForeignKey(
        'hospital_service.Hospital',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sos_responses',
    )

    # Location at time of SOS
    latitude    = models.DecimalField(max_digits=10, decimal_places=7)
    longitude   = models.DecimalField(max_digits=10, decimal_places=7)
    address     = models.TextField(blank=True)     # reverse-geocoded address if available

    # Medical context
    severity    = models.CharField(max_length=20, choices=Severity.choices, default=Severity.HIGH)
    description = models.TextField(blank=True)     # patient's description of emergency
    blood_group = models.CharField(max_length=10, blank=True)
    allergies   = models.TextField(blank=True)
    medications = models.TextField(blank=True)

    # Emergency contact (pulled from patient profile or entered manually)
    emergency_contact_name  = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Hospital response tracking
    accepted_at     = models.DateTimeField(null=True, blank=True)
    enroute_at      = models.DateTimeField(null=True, blank=True)
    arrived_at      = models.DateTimeField(null=True, blank=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)

    # ETA from hospital (minutes)
    eta_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Ambulance tracking (hospital updates this live)
    ambulance_latitude  = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ambulance_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ambulance_number    = models.CharField(max_length=50, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sos_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f'SOS #{self.pk} — {self.patient.full_name} [{self.status}]'


class SOSStatusLog(models.Model):
    """Immutable audit trail of every status change."""
    sos         = models.ForeignKey(SOSAlert, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=20, blank=True)
    to_status   = models.CharField(max_length=20)
    changed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    note        = models.TextField(blank=True)
    changed_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sos_status_logs'
        ordering = ['changed_at']