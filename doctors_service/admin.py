from django.contrib import admin
from .models import DoctorProfile, WeeklySchedule, SlotBlock, TimeSlot, DoctorReview

class WeeklyScheduleInline(admin.TabularInline):
    model = WeeklySchedule
    extra = 0

class SlotBlockInline(admin.TabularInline):
    model = SlotBlock
    extra = 0

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display  = ['__str__','specialization','experience_years','consultation_fee','rating','is_available_today']
    list_filter   = ['specialization','is_available_today']
    search_fields = ['user__full_name','license_number']
    inlines       = [WeeklyScheduleInline, SlotBlockInline]

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor','date','start_time','end_time','status']
    list_filter  = ['status','date']