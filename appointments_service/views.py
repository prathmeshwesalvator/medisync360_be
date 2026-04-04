from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer, AppointmentListSerializer,
    AppointmentDetailSerializer, RescheduleSerializer, CancelSerializer,
    ConfirmAppointmentSerializer, CompleteAppointmentSerializer,
    UpdateNotesSerializer,
)
from .appointment_service import (
    create_appointment, cancel_appointment, reschedule_appointment,
    mark_paid, confirm_appointment, complete_appointment,
    mark_no_show, update_visit_notes,
)
from utils.response import success_response, error_response
from utils.permission import IsDoctorRole, IsHospitalRole


# ── Patient endpoints ─────────────────────────────────────────────────────────

class BookAppointmentView(APIView):
    """POST /api/appointments/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = AppointmentCreateSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = create_appointment(
                patient=request.user,
                doctor=s.validated_data['doctor_obj'],
                slot=s.validated_data['slot'],
                reason=s.validated_data.get('reason', ''),
                symptoms=s.validated_data.get('symptoms', ''),
                appointment_type=s.validated_data.get('appointment_type', 'in_person'),
            )
        except Exception as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment booked. Waiting for doctor confirmation.',
            status_code=201,
        )


class MyAppointmentsView(APIView):
    """GET /api/appointments/my/?status=&type="""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Appointment.objects.filter(patient=request.user).select_related(
            'doctor__user', 'hospital'
        ).prefetch_related('status_logs')
        if status_filter := request.query_params.get('status'):
            qs = qs.filter(status=status_filter)
        if type_filter := request.query_params.get('type'):
            qs = qs.filter(appointment_type=type_filter)
        return success_response(data=AppointmentListSerializer(qs, many=True).data)


class PatientAppointmentStatsView(APIView):
    """GET /api/appointments/my/stats/ — dashboard summary counts"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Appointment.objects.filter(patient=request.user)
        stats = qs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            confirmed=Count('id', filter=Q(status='confirmed')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            upcoming=Count('id', filter=Q(status__in=['pending', 'confirmed'])),
        )
        return success_response(data=stats)


class AppointmentDetailView(APIView):
    """GET /api/appointments/<pk>/"""
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk):
        try:
            appt = Appointment.objects.select_related(
                'doctor__user', 'hospital', 'patient'
            ).prefetch_related('status_logs').get(pk=pk)
        except Appointment.DoesNotExist:
            return None
        user = request.user
        if not (
            appt.patient == user
            or (hasattr(user, 'doctor_profile') and appt.doctor.user == user)
            or (hasattr(user, 'hospital') and appt.hospital and appt.hospital.user == user)
            or user.role == 'admin'
        ):
            return None
        return appt

    def get(self, request, pk):
        appt = self._get(request, pk)
        if not appt:
            return error_response('Appointment not found.', status_code=404)
        return success_response(data=AppointmentDetailSerializer(appt).data)


class CancelAppointmentView(APIView):
    """POST /api/appointments/<pk>/cancel/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return error_response('Appointment not found.', status_code=404)
        s = CancelSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = cancel_appointment(appt, s.validated_data.get('reason', ''),
                                      changed_by=request.user)
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment cancelled.',
        )


class RescheduleAppointmentView(APIView):
    """POST /api/appointments/<pk>/reschedule/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return error_response('Appointment not found.', status_code=404)
        s = RescheduleSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = reschedule_appointment(appt, s.validated_data['slot_id'],
                                          changed_by=request.user)
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment rescheduled. Waiting for doctor re-confirmation.',
        )


class MarkPaidView(APIView):
    """POST /api/appointments/<pk>/pay/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return error_response('Appointment not found.', status_code=404)
        if appt.payment_status == 'paid':
            return error_response('Already marked as paid.')
        appt = mark_paid(appt)
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Payment recorded.',
        )


# ── Doctor endpoints ──────────────────────────────────────────────────────────

class DoctorAppointmentsView(APIView):
    """GET /api/appointments/doctor/mine/?status=&date="""
    permission_classes = [IsDoctorRole]

    def get(self, request):
        try:
            doc = request.user.doctor_profile
        except Exception:
            return error_response('Doctor profile not found.', status_code=404)
        qs = Appointment.objects.filter(doctor=doc).select_related(
            'patient', 'hospital'
        ).prefetch_related('status_logs')
        if status_filter := request.query_params.get('status'):
            qs = qs.filter(status=status_filter)
        if date_filter := request.query_params.get('date'):
            qs = qs.filter(date=date_filter)
        return success_response(data=AppointmentListSerializer(qs, many=True).data)


class DoctorAppointmentStatsView(APIView):
    """GET /api/appointments/doctor/stats/ — doctor dashboard counts"""
    permission_classes = [IsDoctorRole]

    def get(self, request):
        try:
            doc = request.user.doctor_profile
        except Exception:
            return error_response('Doctor profile not found.', status_code=404)
        from django.utils import timezone
        today = timezone.now().date()
        qs = Appointment.objects.filter(doctor=doc)
        stats = qs.aggregate(
            total=Count('id'),
            today_total=Count('id', filter=Q(date=today)),
            today_pending=Count('id', filter=Q(date=today, status='pending')),
            today_confirmed=Count('id', filter=Q(date=today, status='confirmed')),
            today_completed=Count('id', filter=Q(date=today, status='completed')),
            pending_confirmation=Count('id', filter=Q(status='pending')),
        )
        return success_response(data=stats)


class ConfirmAppointmentView(APIView):
    """POST /api/appointments/<pk>/confirm/"""
    permission_classes = [IsDoctorRole]

    def post(self, request, pk):
        try:
            doc  = request.user.doctor_profile
            appt = Appointment.objects.get(pk=pk, doctor=doc)
        except Exception:
            return error_response('Appointment not found.', status_code=404)
        s = ConfirmAppointmentSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = confirm_appointment(
                appt,
                doctor_user=request.user,
                meeting_link=s.validated_data.get('meeting_link', ''),
            )
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment confirmed.',
        )


class CompleteAppointmentView(APIView):
    """POST /api/appointments/<pk>/complete/"""
    permission_classes = [IsDoctorRole]

    def post(self, request, pk):
        try:
            doc  = request.user.doctor_profile
            appt = Appointment.objects.get(pk=pk, doctor=doc)
        except Exception:
            return error_response('Appointment not found.', status_code=404)
        s = CompleteAppointmentSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = complete_appointment(
                appt,
                doctor_user=request.user,
                notes=s.validated_data.get('notes', ''),
                diagnosis=s.validated_data.get('diagnosis', ''),
                prescription=s.validated_data.get('prescription', ''),
            )
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment completed.',
        )


class NoShowView(APIView):
    """POST /api/appointments/<pk>/no-show/"""
    permission_classes = [IsDoctorRole]

    def post(self, request, pk):
        try:
            doc  = request.user.doctor_profile
            appt = Appointment.objects.get(pk=pk, doctor=doc)
        except Exception:
            return error_response('Appointment not found.', status_code=404)
        try:
            appt = mark_no_show(appt, request.user)
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment marked as no-show.',
        )


class UpdateNotesView(APIView):
    """PATCH /api/appointments/<pk>/notes/"""
    permission_classes = [IsDoctorRole]

    def patch(self, request, pk):
        try:
            doc  = request.user.doctor_profile
            appt = Appointment.objects.get(pk=pk, doctor=doc)
        except Exception:
            return error_response('Appointment not found.', status_code=404)
        s = UpdateNotesSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = update_visit_notes(
                appt,
                doctor_user=request.user,
                notes=s.validated_data.get('notes', ''),
                diagnosis=s.validated_data.get('diagnosis', ''),
                prescription=s.validated_data.get('prescription', ''),
            )
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Visit notes updated.',
        )


# ── Hospital endpoints ────────────────────────────────────────────────────────

class HospitalAppointmentsView(APIView):
    """GET /api/appointments/hospital/mine/?status=&date="""
    permission_classes = [IsHospitalRole]

    def get(self, request):
        try:
            hospital = request.user.hospital
        except Exception:
            return error_response('Hospital profile not found.', status_code=404)
        qs = Appointment.objects.filter(hospital=hospital).select_related(
            'doctor__user', 'patient'
        ).prefetch_related('status_logs')
        if status_filter := request.query_params.get('status'):
            qs = qs.filter(status=status_filter)
        if date_filter := request.query_params.get('date'):
            qs = qs.filter(date=date_filter)
        return success_response(data=AppointmentListSerializer(qs, many=True).data)