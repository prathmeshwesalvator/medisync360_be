from django.contrib import admin
from .models import SOSAlert, SOSStatusLog

class SOSStatusLogInline(admin.TabularInline):
    model = SOSStatusLog
    extra = 0
    readonly_fields = ['from_status','to_status','changed_by','note','changed_at']

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display  = ['id','patient','status','severity','responding_hospital','created_at']
    list_filter   = ['status','severity']
    search_fields = ['patient__full_name','patient__email']
    inlines       = [SOSStatusLogInline]