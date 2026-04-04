import datetime
from django.utils import timezone
from .models import Appointment, AppointmentStatusLog, AppointmentReminder
from doctors_service.models import TimeSlot


# ── Internal helper ───────────────────────────────────────────────────────────

def _log(appt: Appointment, to_status: str, changed_by=None, reason: str = '') -> None:
    """Write one immutable status-change record."""
    AppointmentStatusLog.objects.create(
        appointment=appt,
        from_status=appt.status,
        to_status=to_status,
        changed_by=changed_by,
        reason=reason,
    )


def _schedule_reminders(appt: Appointment) -> None:
    """Create 24h and 1h reminder records (replace existing)."""
    appt.reminders.all().delete()
    appt_dt = datetime.datetime.combine(appt.date, appt.start_time)
    appt_dt = timezone.make_aware(appt_dt)
    AppointmentReminder.objects.bulk_create([
        AppointmentReminder(appointment=appt, remind_at=appt_dt - datetime.timedelta(days=1)),
        AppointmentReminder(appointment=appt, remind_at=appt_dt - datetime.timedelta(hours=1)),
    ])


# ── Patient actions ───────────────────────────────────────────────────────────

def create_appointment(
    patient,
    doctor,
    slot,
    reason: str = '',
    symptoms: str = '',
    appointment_type: str = 'in_person',
) -> Appointment:
    """
    Book a new appointment.
    - Marks the slot as 'booked'.
    - Creates 24h + 1h reminder records.
    - Writes the first status log entry.
    - Status starts as PENDING (doctor must confirm).
    """
    appt = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        hospital=doctor.hospital,
        time_slot=slot,
        date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        appointment_type=appointment_type,
        status=Appointment.Status.PENDING,
        reason=reason,
        symptoms=symptoms,
        consultation_fee=doctor.consultation_fee,
    )
    slot.status = 'booked'
    slot.save(update_fields=['status'])
    _log(appt, Appointment.Status.PENDING, changed_by=patient,
         reason='Appointment booked by patient')
    _schedule_reminders(appt)
    return appt


def cancel_appointment(appt: Appointment, reason: str = '', changed_by=None) -> Appointment:
    """Patient or doctor cancels. Frees the slot."""
    if appt.status in (Appointment.Status.COMPLETED, Appointment.Status.CANCELLED):
        raise ValueError('Cannot cancel a completed or already cancelled appointment.')
    if appt.time_slot:
        appt.time_slot.status = 'available'
        appt.time_slot.save(update_fields=['status'])
    _log(appt, Appointment.Status.CANCELLED, changed_by=changed_by, reason=reason)
    appt.status = Appointment.Status.CANCELLED
    appt.cancel_reason = reason
    appt.save(update_fields=['status', 'cancel_reason', 'updated_at'])
    return appt


def reschedule_appointment(appt: Appointment, new_slot: TimeSlot, changed_by=None) -> Appointment:
    """Move appointment to a new slot. Frees old slot, books new one."""
    if appt.status in (Appointment.Status.COMPLETED, Appointment.Status.CANCELLED):
        raise ValueError('Cannot reschedule a completed or cancelled appointment.')
    if appt.reschedule_count >= 3:
        raise ValueError('Maximum reschedule limit (3) reached.')
    # Free old slot
    if appt.time_slot:
        appt.time_slot.status = 'available'
        appt.time_slot.save(update_fields=['status'])
    # Book new slot
    new_slot.status = 'booked'
    new_slot.save(update_fields=['status'])
    _log(appt, Appointment.Status.RESCHEDULED, changed_by=changed_by,
         reason=f'Rescheduled to {new_slot.date} {new_slot.start_time}')
    appt.time_slot      = new_slot
    appt.date           = new_slot.date
    appt.start_time     = new_slot.start_time
    appt.end_time       = new_slot.end_time
    appt.status         = Appointment.Status.RESCHEDULED
    appt.reschedule_count += 1
    appt.confirmed_at   = None   # requires re-confirmation after reschedule
    appt.save(update_fields=[
        'time_slot', 'date', 'start_time', 'end_time',
        'status', 'reschedule_count', 'confirmed_at', 'updated_at',
    ])
    _schedule_reminders(appt)
    return appt


def mark_paid(appt: Appointment) -> Appointment:
    appt.payment_status    = Appointment.PaymentStatus.PAID
    appt.payment_marked_at = timezone.now()
    appt.save(update_fields=['payment_status', 'payment_marked_at', 'updated_at'])
    return appt


# ── Doctor actions ────────────────────────────────────────────────────────────

def confirm_appointment(appt: Appointment, doctor_user, meeting_link: str = '') -> Appointment:
    """
    Doctor confirms a pending (or rescheduled) appointment.
    Optionally attaches a video/phone meeting link.
    """
    if appt.status not in (Appointment.Status.PENDING, Appointment.Status.RESCHEDULED):
        raise ValueError('Only pending or rescheduled appointments can be confirmed.')
    _log(appt, Appointment.Status.CONFIRMED, changed_by=doctor_user,
         reason='Confirmed by doctor')
    appt.status       = Appointment.Status.CONFIRMED
    appt.confirmed_at = timezone.now()
    if meeting_link:
        appt.meeting_link = meeting_link
    appt.save(update_fields=['status', 'confirmed_at', 'meeting_link', 'updated_at'])
    return appt


def complete_appointment(
    appt: Appointment,
    doctor_user,
    notes: str = '',
    diagnosis: str = '',
    prescription: str = '',
) -> Appointment:
    """
    Doctor marks appointment as completed and optionally records
    visit notes, diagnosis, and a prescription summary.
    """
    if appt.status not in (Appointment.Status.CONFIRMED, Appointment.Status.RESCHEDULED):
        raise ValueError('Only confirmed appointments can be completed.')
    _log(appt, Appointment.Status.COMPLETED, changed_by=doctor_user,
         reason='Marked completed by doctor')
    appt.status       = Appointment.Status.COMPLETED
    appt.completed_at = timezone.now()
    if notes:
        appt.notes = notes
    if diagnosis:
        appt.diagnosis = diagnosis
    if prescription:
        appt.prescription = prescription
    appt.save(update_fields=[
        'status', 'completed_at', 'notes', 'diagnosis', 'prescription', 'updated_at',
    ])
    return appt


def mark_no_show(appt: Appointment, doctor_user) -> Appointment:
    """Doctor marks patient as no-show. Slot is freed."""
    if appt.status != Appointment.Status.CONFIRMED:
        raise ValueError('Only confirmed appointments can be marked no-show.')
    if appt.time_slot:
        appt.time_slot.status = 'available'
        appt.time_slot.save(update_fields=['status'])
    _log(appt, Appointment.Status.NO_SHOW, changed_by=doctor_user,
         reason='Patient did not show up')
    appt.status = Appointment.Status.NO_SHOW
    appt.save(update_fields=['status', 'updated_at'])
    return appt


def update_visit_notes(
    appt: Appointment,
    doctor_user,
    notes: str = '',
    diagnosis: str = '',
    prescription: str = '',
) -> Appointment:
    """
    Doctor updates clinical notes on a completed appointment.
    Can be called any number of times post-completion.
    """
    if appt.status != Appointment.Status.COMPLETED:
        raise ValueError('Notes can only be updated on completed appointments.')
    update_fields = ['updated_at']
    if notes is not None:
        appt.notes = notes
        update_fields.append('notes')
    if diagnosis is not None:
        appt.diagnosis = diagnosis
        update_fields.append('diagnosis')
    if prescription is not None:
        appt.prescription = prescription
        update_fields.append('prescription')
    appt.save(update_fields=update_fields)
    return appt