import threading
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import LabReport, ReportQuestion
from .serializers import (
    LabReportSerializer,
    LabReportUploadSerializer,
    LabReportListSerializer,
    ReportQuestionSerializer,
    AskQuestionSerializer,
)
from .lab_service import process_lab_report, ask_followup_question


def _run_analysis(report: LabReport):
    """Background thread: run OCR + GPT and save results."""
    report.status = 'processing'
    report.save(update_fields=['status'])

    result = process_lab_report(
        image_path=report.image.path,
        report_type=report.report_type,
    )

    if 'error' in result and not result.get('ai_result'):
        report.status = 'failed'
        report.ocr_raw_text = result.get('error', '')
    else:
        report.status = 'completed'
        report.ocr_raw_text = result.get('ocr_text', '')
        report.extracted_data = result.get('extracted_params', {})
        report.ai_structured_result = result.get('ai_result', {})
        report.ai_analysis = result.get('ai_result', {}).get('summary', '')

    report.save()


class LabReportUploadView(APIView):
    """
    POST /lab-reports/upload/
    Upload a lab report image. Analysis runs async in background.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = LabReportUploadSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save(user=request.user, status='pending')
            # Fire-and-forget analysis
            thread = threading.Thread(target=_run_analysis, args=(report,), daemon=True)
            thread.start()
            return Response(
                {
                    "message": "Report uploaded. Analysis is in progress.",
                    "report_id": report.id,
                    "status": report.status,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabReportListView(generics.ListAPIView):
    """
    GET /lab-reports/
    List all reports for authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LabReportListSerializer

    def get_queryset(self):
        return LabReport.objects.filter(user=self.request.user)


class LabReportDetailView(generics.RetrieveAPIView):
    """
    GET /lab-reports/<id>/
    Full detail of a single report including AI analysis.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LabReportSerializer

    def get_queryset(self):
        return LabReport.objects.filter(user=self.request.user)


class LabReportDeleteView(generics.DestroyAPIView):
    """
    DELETE /lab-reports/<id>/delete/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LabReport.objects.filter(user=self.request.user)


class LabReportStatusView(APIView):
    """
    GET /lab-reports/<id>/status/
    Poll processing status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            report = LabReport.objects.get(pk=pk, user=request.user)
            return Response({"id": report.id, "status": report.status})
        except LabReport.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class AskQuestionView(APIView):
    """
    POST /lab-reports/<id>/ask/
    Ask a follow-up question about a specific report.
    Body: { "question": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            report = LabReport.objects.get(pk=pk, user=request.user)
        except LabReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        if report.status != 'completed':
            return Response(
                {"error": "Report analysis is not complete yet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        question_text = serializer.validated_data['question']
        answer = ask_followup_question(
            report_context=report.ai_structured_result or {},
            question=question_text,
        )

        qa = ReportQuestion.objects.create(
            report=report,
            user=request.user,
            question=question_text,
            answer=answer,
        )
        return Response(ReportQuestionSerializer(qa).data)


class ReportQuestionsListView(generics.ListAPIView):
    """
    GET /lab-reports/<pk>/questions/
    Retrieve all Q&A for a report.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportQuestionSerializer

    def get_queryset(self):
        return ReportQuestion.objects.filter(
            report_id=self.kwargs['pk'],
            user=self.request.user
        )


class ReportSummaryView(APIView):
    """
    GET /lab-reports/<id>/summary/
    Returns a lightweight health summary card for the mobile dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            report = LabReport.objects.get(pk=pk, user=request.user)
        except LabReport.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if report.status != 'completed' or not report.ai_structured_result:
            return Response({"status": report.status, "message": "Analysis pending"})

        result = report.ai_structured_result
        return Response({
            "id": report.id,
            "report_type": result.get("report_type", report.report_type),
            "uploaded_at": report.uploaded_at,
            "summary": result.get("summary", ""),
            "abnormal_flags": result.get("abnormal_flags", []),
            "critical_alerts": result.get("critical_alerts", []),
            "doctor_consult_urgency": result.get("doctor_consult_urgency", "routine"),
            "doctor_consult_reason": result.get("doctor_consult_reason", ""),
        })