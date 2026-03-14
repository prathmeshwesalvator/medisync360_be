import datetime
from .models import DoctorProfile, WeeklySchedule, SlotBlock, TimeSlot


def generate_slots_for_date(doctor: DoctorProfile, date: datetime.date) -> list:
    """
    Generate TimeSlot records for a doctor on a given date.
    - Skips if the date is blocked via SlotBlock.
    - Derives slots from the WeeklySchedule for that weekday.
    - Skips slots that already exist.
    """
    if SlotBlock.objects.filter(doctor=doctor, date=date).exists():
        return []

    weekday = date.weekday()
    try:
        schedule = WeeklySchedule.objects.get(doctor=doctor, day_of_week=weekday, is_active=True)
    except WeeklySchedule.DoesNotExist:
        return []

    slots = []
    current = datetime.datetime.combine(date, schedule.start_time)
    end     = datetime.datetime.combine(date, schedule.end_time)
    delta   = datetime.timedelta(minutes=schedule.slot_duration_minutes)

    while current + delta <= end:
        slot_end = current + delta
        obj, created = TimeSlot.objects.get_or_create(
            doctor=doctor,
            date=date,
            start_time=current.time(),
            defaults={'end_time': slot_end.time(), 'status': 'available'},
        )
        if created:
            slots.append(obj)
        current += delta
    return slots


def get_available_slots(doctor: DoctorProfile, date: datetime.date) -> list:
    generate_slots_for_date(doctor, date)
    return list(TimeSlot.objects.filter(doctor=doctor, date=date, status='available'))


def search_doctors(query='', specialization='', city='', available_only=False):
    from .models import DoctorProfile
    qs = DoctorProfile.objects.select_related('user', 'hospital')
    if query:
        qs = qs.filter(user__full_name__icontains=query)
    if specialization:
        qs = qs.filter(specialization=specialization)
    if city:
        qs = qs.filter(hospital__city__icontains=city)
    if available_only:
        qs = qs.filter(is_available_today=True)
    return qs