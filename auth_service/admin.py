from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auth_service.models import User
from doctors_service.models import DoctorProfile
from hospital_service.models  import  Hospital as HospitalProfile


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'


class HospitalProfileInline(admin.StackedInline):
    model = HospitalProfile
    can_delete = False
    verbose_name_plural = 'Hospital Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'approval_status', 'is_active', 'date_joined']
    list_filter = ['role', 'approval_status', 'is_active']
    search_fields = ['email', 'full_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'profile_picture')}),
        ('Role & Status', {'fields': ('role', 'approval_status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined']

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.Role.DOCTOR:
                return [DoctorProfileInline]
            if obj.role == User.Role.HOSPITAL:
                return [HospitalProfileInline]
        return []