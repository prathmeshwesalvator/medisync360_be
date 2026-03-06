from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/',               include('auth_service.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('api/hospitals/',     include('hospital_service.urls')),
    path('api/doctors/',       include('doctors_service.urls')),
    path('api/appointments/',  include('appointments_service.urls')),
    path('api/ehr/',           include('ehr_service.urls')),
    path('api/notifications/', include('notifications_service.urls')),
    path('api/lab-reports/',   include('lab_reports_service.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)