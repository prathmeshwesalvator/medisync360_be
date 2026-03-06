from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import LabReport
from .serializers import LabReportSerializer, LabReportCreateSerializer
from .lab_service import can_access_report
from utils.response import success_response, error_response


class LabReportListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = LabReport.objects.filter(patient=request.user)
        return success_response(data=LabReportSerializer(qs, many=True).data)

    def post(self, request):
        # Patient uploading their own report
        s = LabReportCreateSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        report = s.save(patient=request.user, uploaded_by=request.user)
        return success_response(data=LabReportSerializer(report).data, status_code=201)


class LabReportDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try: report = LabReport.objects.get(pk=pk)
        except LabReport.DoesNotExist: return error_response('Not found.', status_code=404)
        if not can_access_report(request.user, report):
            return error_response('Access denied.', status_code=403)
        return success_response(data=LabReportSerializer(report).data)


class PatientLabReportView(APIView):
    """Doctor or hospital uploads report on behalf of patient."""
    permission_classes = [IsAuthenticated]
    def post(self, request, patient_id):
        from django.contrib.auth import get_user_model
        U = get_user_model()
        try: patient = U.objects.get(pk=patient_id, role='user')
        except: return error_response('Patient not found.', status_code=404)
        s = LabReportCreateSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        report = s.save(
            patient=patient,
            uploaded_by=request.user,
            doctor=getattr(request.user, 'doctor_profile', None),
            hospital=getattr(getattr(request.user, 'hospital', None), None, None),
        )
        try:
            from notifications_service.notification_service import create_notification
            from notifications_service.models import Notification
            create_notification(
                recipient=patient,
                title='Lab Report Uploaded',
                body=f'A new lab report ({report.title}) has been uploaded for you.',
                notif_type=Notification.Type.LAB_REPORT_UPLOADED,
                data={'report_id': report.id},
            )
        except Exception:
            pass
        return success_response(data=LabReportSerializer(report).data, status_code=201)

    def get(self, request, patient_id):
        from django.contrib.auth import get_user_model
        U = get_user_model()
        try: patient = U.objects.get(pk=patient_id, role='user')
        except: return error_response('Patient not found.', status_code=404)
        if request.user.role not in ['doctor','hospital','admin']:
            return error_response('Access denied.', status_code=403)
        qs = LabReport.objects.filter(patient=patient)
        return success_response(data=LabReportSerializer(qs, many=True).data)