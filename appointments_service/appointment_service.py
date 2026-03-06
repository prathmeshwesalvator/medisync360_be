import datetime
from django.utils import timezone
from .models import Appointment, AppointmentReminder
from doctors_service.models import TimeSlot


def create_appointment(patient, doctor, slot, reason='') -> Appointment:
    appt = Appointment.objects.create(
        patient=patient, doctor=doctor,
        hospital=doctor.hospital,
        time_slot=slot,
        date=slot.date, start_time=slot.start_time, end_time=slot.end_time,
        status=Appointment.Status.CONFIRMED,
        reason=reason,
        consultation_fee=doctor.consultation_fee,
    )
    slot.status = TimeSlot.BOOKED
    slot.save(update_fields=['status'])
    # Schedule reminder: 1 day before + 1 hour before
    appt_dt = datetime.datetime.combine(slot.date, slot.start_time)
    appt_dt = timezone.make_aware(appt_dt)
    AppointmentReminder.objects.create(appointment=appt, remind_at=appt_dt - datetime.timedelta(days=1))
    AppointmentReminder.objects.create(appointment=appt, remind_at=appt_dt - datetime.timedelta(hours=1))
    return appt


def cancel_appointment(appt: Appointment, reason='') -> Appointment:
    if appt.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
        raise ValueError('Cannot cancel a completed or already cancelled appointment.')
    # Free the slot
    if appt.time_slot:
        appt.time_slot.status = TimeSlot.AVAILABLE
        appt.time_slot.save(update_fields=['status'])
    appt.status = Appointment.Status.CANCELLED
    appt.cancel_reason = reason
    appt.save(update_fields=['status','cancel_reason','updated_at'])
    return appt


def reschedule_appointment(appt: Appointment, new_slot: TimeSlot) -> Appointment:
    if appt.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
        raise ValueError('Cannot reschedule a completed or cancelled appointment.')
    # Free old slot
    if appt.time_slot:
        appt.time_slot.status = TimeSlot.AVAILABLE
        appt.time_slot.save(update_fields=['status'])
    # Book new slot
    new_slot.status = TimeSlot.BOOKED
    new_slot.save(update_fields=['status'])
    appt.time_slot  = new_slot
    appt.date       = new_slot.date
    appt.start_time = new_slot.start_time
    appt.end_time   = new_slot.end_time
    appt.status     = Appointment.Status.RESCHEDULED
    appt.reschedule_count += 1
    appt.save(update_fields=['time_slot','date','start_time','end_time','status','reschedule_count','updated_at'])
    # Reset reminders
    appt.reminders.all().delete()
    appt_dt = datetime.datetime.combine(new_slot.date, new_slot.start_time)
    appt_dt = timezone.make_aware(appt_dt)
    AppointmentReminder.objects.create(appointment=appt, remind_at=appt_dt - datetime.timedelta(days=1))
    AppointmentReminder.objects.create(appointment=appt, remind_at=appt_dt - datetime.timedelta(hours=1))
    return appt


def mark_paid(appt: Appointment) -> Appointment:
    appt.payment_status    = Appointment.PaymentStatus.PAID
    appt.payment_marked_at = timezone.now()
    appt.save(update_fields=['payment_status','payment_marked_at','updated_at'])
    return appt