from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import (AppointmentCreateSerializer, AppointmentListSerializer,
    AppointmentDetailSerializer, RescheduleSerializer, CancelSerializer)
from .appointment_service import (create_appointment, cancel_appointment,
    reschedule_appointment, mark_paid)
from utils.response import success_response, error_response
from utils.permission import IsDoctorRole


class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = AppointmentCreateSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            appt = create_appointment(
                patient=request.user,
                # FIX: key is now 'doctor_obj' (the DoctorProfile instance)
                doctor=s.validated_data['doctor_obj'],
                slot=s.validated_data['slot'],
                reason=s.validated_data.get('reason', ''),
            )
        except Exception as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment booked.',
            status_code=201,
        )


class MyAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status')
        qs = Appointment.objects.filter(patient=request.user).select_related(
            'doctor__user', 'hospital'
        )
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(data=AppointmentListSerializer(qs, many=True).data)


class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk):
        try:
            appt = Appointment.objects.select_related(
                'doctor__user', 'hospital', 'patient'
            ).get(pk=pk)
        except Appointment.DoesNotExist:
            return None
        user = request.user
        if not (appt.patient == user or
                (hasattr(user, 'doctor_profile') and appt.doctor.user == user) or
                (hasattr(user, 'hospital') and appt.hospital and appt.hospital.user == user) or
                user.role == 'admin'):
            return None
        return appt

    def get(self, request, pk):
        appt = self._get(request, pk)
        if not appt:
            return error_response('Appointment not found.', status_code=404)
        return success_response(data=AppointmentDetailSerializer(appt).data)


class CancelAppointmentView(APIView):
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
            appt = cancel_appointment(appt, s.validated_data.get('reason', ''))
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment cancelled.',
        )


class RescheduleAppointmentView(APIView):
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
            # FIX: validate_slot_id now returns the TimeSlot object directly
            appt = reschedule_appointment(appt, s.validated_data['slot_id'])
        except ValueError as e:
            return error_response(str(e))
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment rescheduled.',
        )


class MarkPaidView(APIView):
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


class DoctorAppointmentsView(APIView):
    permission_classes = [IsDoctorRole]

    def get(self, request):
        try:
            doc = request.user.doctor_profile
        except Exception:
            return error_response('Doctor profile not found.', status_code=404)
        status_filter = request.query_params.get('status')
        qs = Appointment.objects.filter(doctor=doc).select_related('patient', 'hospital')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(data=AppointmentListSerializer(qs, many=True).data)


class CompleteAppointmentView(APIView):
    permission_classes = [IsDoctorRole]

    def post(self, request, pk):
        try:
            doc  = request.user.doctor_profile
            appt = Appointment.objects.get(pk=pk, doctor=doc)
        except Exception:
            return error_response('Appointment not found.', status_code=404)
        if appt.status not in ('confirmed', 'rescheduled'):
            return error_response('Only confirmed appointments can be completed.')
        appt.status = Appointment.Status.COMPLETED
        appt.notes  = request.data.get('notes', appt.notes)
        appt.save(update_fields=['status', 'notes', 'updated_at'])
        return success_response(
            data=AppointmentDetailSerializer(appt).data,
            message='Appointment completed.',
        )