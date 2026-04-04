from django.urls import path
from .views import (
    BookAppointmentView, MyAppointmentsView, PatientAppointmentStatsView,
    AppointmentDetailView,
    CancelAppointmentView, RescheduleAppointmentView, MarkPaidView,
    DoctorAppointmentsView, DoctorAppointmentStatsView,
    ConfirmAppointmentView, CompleteAppointmentView,
    NoShowView, UpdateNotesView,
    HospitalAppointmentsView,
)

urlpatterns = [
    # ── Patient ───────────────────────────────────────────────────────────────
    path('',                                BookAppointmentView.as_view(),         name='book-appointment'),
    path('my/',                             MyAppointmentsView.as_view(),          name='my-appointments'),
    path('my/stats/',                       PatientAppointmentStatsView.as_view(), name='my-appointment-stats'),
    path('<int:pk>/',                       AppointmentDetailView.as_view(),       name='appointment-detail'),
    path('<int:pk>/cancel/',                CancelAppointmentView.as_view(),       name='cancel-appointment'),
    path('<int:pk>/reschedule/',            RescheduleAppointmentView.as_view(),   name='reschedule-appointment'),
    path('<int:pk>/pay/',                   MarkPaidView.as_view(),                name='mark-paid'),

    # ── Doctor ────────────────────────────────────────────────────────────────
    path('doctor/mine/',                    DoctorAppointmentsView.as_view(),      name='doctor-appointments'),
    path('doctor/stats/',                   DoctorAppointmentStatsView.as_view(),  name='doctor-appointment-stats'),
    path('<int:pk>/confirm/',               ConfirmAppointmentView.as_view(),      name='confirm-appointment'),
    path('<int:pk>/complete/',              CompleteAppointmentView.as_view(),     name='complete-appointment'),
    path('<int:pk>/no-show/',               NoShowView.as_view(),                  name='no-show-appointment'),
    path('<int:pk>/notes/',                 UpdateNotesView.as_view(),             name='update-notes'),

    # ── Hospital ──────────────────────────────────────────────────────────────
    path('hospital/mine/',                  HospitalAppointmentsView.as_view(),    name='hospital-appointments'),
]