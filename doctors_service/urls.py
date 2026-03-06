from django.urls import path
from .views import (DoctorListView, DoctorDetailView, DoctorAvailableSlotsView,
    MyDoctorProfileView, MyWeeklyScheduleView, SlotBlockView, DoctorReviewView)

urlpatterns = [
    path('',                                    DoctorListView.as_view(),           name='doctor-list'),
    path('<int:pk>/',                           DoctorDetailView.as_view(),         name='doctor-detail'),
    path('<int:pk>/slots/',                     DoctorAvailableSlotsView.as_view(), name='doctor-slots'),
    path('<int:pk>/reviews/',                   DoctorReviewView.as_view(),         name='doctor-reviews'),
    path('my/',                                 MyDoctorProfileView.as_view(),      name='my-doctor-profile'),
    path('my/schedule/',                        MyWeeklyScheduleView.as_view(),     name='my-schedule'),
    path('my/schedule/<int:day>/',              MyWeeklyScheduleView.as_view(),     name='my-schedule-day'),
    path('my/blocks/',                          SlotBlockView.as_view(),            name='my-blocks'),
    path('my/blocks/<int:block_id>/',           SlotBlockView.as_view(),            name='my-block-detail'),
]