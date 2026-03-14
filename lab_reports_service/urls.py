from django.urls import path
from .views import (
    LabReportUploadView,
    LabReportListView,
    LabReportDetailView,
    LabReportDeleteView,
    LabReportStatusView,
    AskQuestionView,
    ReportQuestionsListView,
    ReportSummaryView,
)

urlpatterns = [
    path('', LabReportListView.as_view(), name='lab-report-list'),
    path('upload/', LabReportUploadView.as_view(), name='lab-report-upload'),
    path('<int:pk>/', LabReportDetailView.as_view(), name='lab-report-detail'),
    path('<int:pk>/delete/', LabReportDeleteView.as_view(), name='lab-report-delete'),
    path('<int:pk>/status/', LabReportStatusView.as_view(), name='lab-report-status'),
    path('<int:pk>/ask/', AskQuestionView.as_view(), name='lab-report-ask'),
    path('<int:pk>/questions/', ReportQuestionsListView.as_view(), name='lab-report-questions'),
    path('<int:pk>/summary/', ReportSummaryView.as_view(), name='lab-report-summary'),
]