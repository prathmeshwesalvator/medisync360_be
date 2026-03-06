from django.urls import path
from .views import (MedicalHistoryView, PrescriptionListView, PrescriptionCreateView,
    DoctorNoteListView, ImagingRecordView)

urlpatterns = [
    # Own records
    path('my/history/',                         MedicalHistoryView.as_view(),       name='my-history'),
    path('my/prescriptions/',                   PrescriptionListView.as_view(),     name='my-prescriptions'),
    path('my/notes/',                           DoctorNoteListView.as_view(),       name='my-notes'),
    path('my/imaging/',                         ImagingRecordView.as_view(),        name='my-imaging'),
    # Doctor/hospital accessing patient records
    path('patient/<int:patient_id>/history/',   MedicalHistoryView.as_view(),       name='patient-history'),
    path('patient/<int:patient_id>/prescriptions/', PrescriptionListView.as_view(), name='patient-prescriptions'),
    path('patient/<int:patient_id>/prescriptions/add/', PrescriptionCreateView.as_view(), name='add-prescription'),
    path('patient/<int:patient_id>/notes/',     DoctorNoteListView.as_view(),       name='patient-notes'),
    path('patient/<int:patient_id>/notes/add/', DoctorNoteListView.as_view(),       name='add-note'),
    path('patient/<int:patient_id>/imaging/',   ImagingRecordView.as_view(),        name='patient-imaging'),
    path('patient/<int:patient_id>/imaging/add/', ImagingRecordView.as_view(),      name='add-imaging'),
    # Self update
    path('history/update/',                     MedicalHistoryView.as_view(),       name='update-history'),
    path('imaging/upload/',                     ImagingRecordView.as_view(),        name='upload-imaging'),
]