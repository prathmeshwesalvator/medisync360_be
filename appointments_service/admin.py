from django.contrib import admin
from .models import Appointment, AppointmentReminder

class ReminderInline(admin.TabularInline):
    model = AppointmentReminder
    extra = 0
    readonly_fields = ['sent','sent_at']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['id','patient','doctor','date','start_time','status','payment_status']
    list_filter   = ['status','payment_status','date']
    search_fields = ['patient__full_name','doctor__user__full_name']
    inlines       = [ReminderInline]
    readonly_fields = ['created_at','updated_at']