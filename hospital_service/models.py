from django.db import models
from django.conf import settings


class Hospital(models.Model):
    class Status(models.TextChoices):
        ACTIVE      = 'active',      'Active'
        INACTIVE    = 'inactive',    'Inactive'
        MAINTENANCE = 'maintenance', 'Under Maintenance'

    # Directly linked to the User (hospital role)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hospital',
        limit_choices_to={'role': 'hospital'},
    )

    name                = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    description         = models.TextField(blank=True)

    # Location
    address   = models.TextField()
    city      = models.CharField(max_length=100)
    state     = models.CharField(max_length=100)
    pincode   = models.CharField(max_length=10)
    latitude  = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Contact
    phone   = models.CharField(max_length=20)
    email   = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Capacity
    total_beds          = models.PositiveIntegerField(default=0)
    available_beds      = models.PositiveIntegerField(default=0)
    icu_total           = models.PositiveIntegerField(default=0)
    icu_available       = models.PositiveIntegerField(default=0)
    emergency_beds      = models.PositiveIntegerField(default=0)
    emergency_available = models.PositiveIntegerField(default=0)

    # Meta
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_verified      = models.BooleanField(default=False)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    logo_url         = models.URLField(blank=True)
    image_url        = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.city})'

    @property
    def bed_occupancy_percent(self):
        if self.total_beds == 0:
            return 0
        return round(((self.total_beds - self.available_beds) / self.total_beds) * 100, 1)

    @property
    def icu_occupancy_percent(self):
        if self.icu_total == 0:
            return 0
        return round(((self.icu_total - self.icu_available) / self.icu_total) * 100, 1)


class Department(models.Model):
    hospital          = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name              = models.CharField(max_length=100)
    head_doctor_name  = models.CharField(max_length=200, blank=True)
    phone_extension   = models.CharField(max_length=20, blank=True)
    floor             = models.CharField(max_length=50, blank=True)
    is_active         = models.BooleanField(default=True)

    class Meta:
        db_table        = 'hospital_departments'
        unique_together = ['hospital', 'name']

    def __str__(self):
        return f'{self.hospital.name} — {self.name}'


class Amenity(models.Model):
    hospital     = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='amenities')
    name         = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'hospital_amenities'


class CapacityLog(models.Model):
    hospital        = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='capacity_logs')
    total_beds      = models.PositiveIntegerField()
    available_beds  = models.PositiveIntegerField()
    icu_total       = models.PositiveIntegerField()
    icu_available   = models.PositiveIntegerField()
    logged_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'capacity_logs'
        ordering = ['-logged_at']