from django.db import models
from django.conf import settings


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        CONFIRMED  = 'confirmed',  'Confirmed'
        COMPLETED  = 'completed',  'Completed'
        CANCELLED  = 'cancelled',  'Cancelled'
        RESCHEDULED= 'rescheduled','Rescheduled'
        NO_SHOW    = 'no_show',    'No Show'

    class PaymentStatus(models.TextChoices):
        UNPAID  = 'unpaid',  'Unpaid'
        PAID    = 'paid',    'Paid'
        REFUNDED= 'refunded','Refunded'

    patient       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor        = models.ForeignKey('doctors_service.DoctorProfile', on_delete=models.CASCADE, related_name='appointments')
    hospital      = models.ForeignKey('hospital_service.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    time_slot     = models.OneToOneField('doctors_service.TimeSlot', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment')
    date          = models.DateField()
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason        = models.TextField(blank=True)
    notes         = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status   = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    payment_marked_at= models.DateTimeField(null=True, blank=True)
    cancel_reason    = models.TextField(blank=True)
    reschedule_count = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-date','-start_time']

    def __str__(self):
        return f'{self.patient} → Dr.{self.doctor} on {self.date}'


class AppointmentReminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    remind_at   = models.DateTimeField()
    sent        = models.BooleanField(default=False)
    sent_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'appointment_reminders'