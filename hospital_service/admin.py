from django.contrib import admin
from .models import Hospital, Department, Amenity, CapacityLog


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0


class AmenityInline(admin.TabularInline):
    model = Amenity
    extra = 0


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display  = ['name', 'city', 'state', 'is_verified', 'status', 'total_beds', 'available_beds']
    list_filter   = ['status', 'is_verified', 'city', 'state']
    search_fields = ['name', 'city', 'registration_number']
    inlines       = [DepartmentInline, AmenityInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CapacityLog)
class CapacityLogAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'available_beds', 'icu_available', 'logged_at']
    readonly_fields = ['logged_at']