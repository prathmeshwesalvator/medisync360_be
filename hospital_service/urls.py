
from django.urls import path
from .views import (
    HospitalListView,
    HospitalDetailView,
    NearbyHospitalsView,
    MyHospitalView,
    CapacityUpdateView,
    CapacityLogView,
    DepartmentView,
    DepartmentDetailView,
    AdminHospitalListView,
    AdminVerifyHospitalView,
    HospitalMapView,          
)

urlpatterns = [
    # Public
    path('',                          HospitalListView.as_view(),         name='hospital-list'),
    path('nearby/',                   NearbyHospitalsView.as_view(),       name='hospital-nearby'),
    path('map/',                      HospitalMapView.as_view(),           name='hospital-map'),   
    path('<int:pk>/',                 HospitalDetailView.as_view(),        name='hospital-detail'),

    # Hospital user
    path('my/',                       MyHospitalView.as_view(),            name='hospital-my'),
    path('my/capacity/',              CapacityUpdateView.as_view(),        name='hospital-capacity'),
    path('my/capacity/logs/',         CapacityLogView.as_view(),           name='hospital-capacity-logs'),
    path('my/departments/',           DepartmentView.as_view(),            name='hospital-departments'),
    path('my/departments/<int:dept_id>/', DepartmentDetailView.as_view(), name='hospital-department-detail'),

    # Admin
    path('admin/all/',                AdminHospitalListView.as_view(),     name='hospital-admin-list'),
    path('admin/<int:pk>/verify/',    AdminVerifyHospitalView.as_view(),   name='hospital-admin-verify'),
]