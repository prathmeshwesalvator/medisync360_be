from django.urls import path
from .views import (
    SOSCreateView, SOSDetailView, SOSCancelView, MySOSHistoryView,
    ActiveSOSForHospitalView, SOSRespondView, SOSEnrouteView,
    SOSAmbulanceLocationView, SOSArrivedView, SOSResolveView,
)

urlpatterns = [
    # Patient
    path('',                          SOSCreateView.as_view(),            name='sos-create'),
    path('my/',                       MySOSHistoryView.as_view(),         name='sos-my'),
    path('<int:pk>/',                 SOSDetailView.as_view(),            name='sos-detail'),
    path('<int:pk>/cancel/',          SOSCancelView.as_view(),            name='sos-cancel'),

    # Hospital
    path('hospital/active/',          ActiveSOSForHospitalView.as_view(), name='sos-hospital-active'),
    path('<int:pk>/respond/',         SOSRespondView.as_view(),           name='sos-respond'),
    path('<int:pk>/enroute/',         SOSEnrouteView.as_view(),           name='sos-enroute'),
    path('<int:pk>/location/',        SOSAmbulanceLocationView.as_view(), name='sos-location'),
    path('<int:pk>/arrived/',         SOSArrivedView.as_view(),           name='sos-arrived'),
    path('<int:pk>/resolve/',         SOSResolveView.as_view(),           name='sos-resolve'),
]