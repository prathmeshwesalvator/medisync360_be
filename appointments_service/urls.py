from django.urls import path
from .views import (BookAppointmentView, MyAppointmentsView, AppointmentDetailView,
    CancelAppointmentView, RescheduleAppointmentView, MarkPaidView,
    DoctorAppointmentsView, CompleteAppointmentView)

urlpatterns = [
    path('',                                BookAppointmentView.as_view(),      name='book-appointment'),
    path('my/',                             MyAppointmentsView.as_view(),       name='my-appointments'),
    path('<int:pk>/',                       AppointmentDetailView.as_view(),    name='appointment-detail'),
    path('<int:pk>/cancel/',                CancelAppointmentView.as_view(),    name='cancel-appointment'),
    path('<int:pk>/reschedule/',            RescheduleAppointmentView.as_view(),name='reschedule-appointment'),
    path('<int:pk>/pay/',                   MarkPaidView.as_view(),             name='mark-paid'),
    path('doctor/mine/',                    DoctorAppointmentsView.as_view(),   name='doctor-appointments'),
    path('doctor/<int:pk>/complete/',       CompleteAppointmentView.as_view(),  name='complete-appointment'),
]