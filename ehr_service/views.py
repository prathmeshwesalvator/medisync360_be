from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import MedicalHistory, Prescription, DoctorNote, ImagingRecord
from .serializers import (MedicalHistorySerializer, PrescriptionSerializer,
    PrescriptionWriteSerializer, DoctorNoteSerializer, ImagingRecordSerializer)
from .ehr_service import get_or_create_history, can_access_ehr
from utils.response import success_response, error_response
from utils.permission import IsDoctorRole

User = settings.AUTH_USER_MODEL


def _get_patient(pk, requesting_user):
    from django.contrib.auth import get_user_model
    U = get_user_model()
    try:
        patient = U.objects.get(pk=pk, role='user')
    except U.DoesNotExist:
        return None, error_response('Patient not found.', status_code=404)
    if not can_access_ehr(requesting_user, patient):
        return None, error_response('Access denied.', status_code=403)
    return patient, None


class MedicalHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id=None):
        if patient_id:
            patient, err = _get_patient(patient_id, request.user)
            if err: return err
        else:
            patient = request.user
        history = get_or_create_history(patient)
        return success_response(data=MedicalHistorySerializer(history).data)

    def put(self, request):
        history = get_or_create_history(request.user)
        s = MedicalHistorySerializer(history, data=request.data, partial=True)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        return success_response(data=MedicalHistorySerializer(s.save()).data)


class PrescriptionListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id=None):
        if patient_id:
            patient, err = _get_patient(patient_id, request.user)
            if err: return err
        else:
            patient = request.user
        qs = Prescription.objects.filter(patient=patient).select_related('doctor__user')
        return success_response(data=PrescriptionSerializer(qs, many=True).data)


class PrescriptionCreateView(APIView):
    permission_classes = [IsDoctorRole]
    def post(self, request, patient_id):
        from django.contrib.auth import get_user_model
        U = get_user_model()
        try:
            patient = U.objects.get(pk=patient_id, role='user')
        except U.DoesNotExist:
            return error_response('Patient not found.', status_code=404)
        try:
            doctor = request.user.doctor_profile
        except Exception:
            return error_response('Doctor profile not found.', status_code=404)
        s = PrescriptionWriteSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        prescription = s.save(patient=patient, doctor=doctor)
        # Notify patient
        try:
            from notifications_service.notification_service import create_notification
            from notifications_service.models import Notification
            create_notification(
                recipient=patient,
                title='New Prescription',
                body=f'Dr. {doctor.user.full_name} has added a new prescription.',
                notif_type=Notification.Type.PRESCRIPTION_ADDED,
                data={'prescription_id': prescription.id},
            )
        except Exception:
            pass
        return success_response(data=PrescriptionSerializer(prescription).data, status_code=201)


class DoctorNoteListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id=None):
        if patient_id:
            patient, err = _get_patient(patient_id, request.user)
            if err: return err
            qs = DoctorNote.objects.filter(patient=patient)
            if request.user.role != 'admin':
                qs = qs.filter(is_private=False)
        else:
            patient = request.user
            qs = DoctorNote.objects.filter(patient=patient, is_private=False)
        return success_response(data=DoctorNoteSerializer(qs, many=True).data)

    def post(self, request, patient_id):
        from django.contrib.auth import get_user_model
        U = get_user_model()
        try:
            patient = U.objects.get(pk=patient_id, role='user')
            doctor  = request.user.doctor_profile
        except Exception:
            return error_response('Patient or doctor profile not found.', status_code=404)
        s = DoctorNoteSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        note = s.save(patient=patient, doctor=doctor)
        return success_response(data=DoctorNoteSerializer(note).data, status_code=201)


class ImagingRecordView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id=None):
        if patient_id:
            patient, err = _get_patient(patient_id, request.user)
            if err: return err
        else:
            patient = request.user
        qs = ImagingRecord.objects.filter(patient=patient)
        return success_response(data=ImagingRecordSerializer(qs, many=True).data)

    def post(self, request, patient_id=None):
        if patient_id:
            from django.contrib.auth import get_user_model
            U = get_user_model()
            try: patient = U.objects.get(pk=patient_id, role='user')
            except: return error_response('Patient not found.', status_code=404)
            if not can_access_ehr(request.user, patient):
                return error_response('Access denied.', status_code=403)
        else:
            patient = request.user
        s = ImagingRecordSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        record = s.save(
            patient=patient,
            doctor=getattr(request.user, 'doctor_profile', None),
            hospital=getattr(request.user, 'hospital', None),
        )
        return success_response(data=ImagingRecordSerializer(record).data, status_code=201)