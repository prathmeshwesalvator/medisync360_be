from django.urls import path
from .views import LabReportListView, LabReportDetailView, PatientLabReportView

urlpatterns = [
    path('',                                    LabReportListView.as_view(),    name='lab-report-list'),
    path('<int:pk>/',                           LabReportDetailView.as_view(), name='lab-report-detail'),
    path('patient/<int:patient_id>/',           PatientLabReportView.as_view(),name='patient-lab-reports'),
    path('patient/<int:patient_id>/upload/',    PatientLabReportView.as_view(),name='upload-for-patient'),
]