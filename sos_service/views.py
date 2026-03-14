from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SOSAlert
from .serializers import (
    SOSAlertSerializer, SOSCreateSerializer,
    SOSRespondSerializer, SOSAmbulanceUpdateSerializer,
)
from .sos_service import (
    create_sos, hospital_accept_sos, hospital_enroute_sos,
    update_ambulance_location, hospital_arrived_sos,
    resolve_sos, cancel_sos, get_active_sos_for_hospital,
)
from hospital_service.models import Hospital
from utils.response import success_response, error_response
from utils.permission import IsHospitalRole


# ── Patient endpoints ─────────────────────────────────────────────────────────

class SOSCreateView(APIView):
    """POST /api/sos/ — patient fires SOS."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'user':
            return error_response('Only patients can trigger SOS.')
        s = SOSCreateSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        sos = create_sos(request.user, s.validated_data)
        return success_response(
            data=SOSAlertSerializer(sos).data,
            message='SOS alert sent. Nearby hospitals have been notified.',
            status_code=201,
        )


class SOSDetailView(APIView):
    """GET /api/sos/<pk>/ — patient polls for status + ambulance location."""
    permission_classes = [IsAuthenticated]

    def _get_sos(self, request, pk):
        try:
            sos = SOSAlert.objects.get(pk=pk)
        except SOSAlert.DoesNotExist:
            return None
        user = request.user
        # Patient who created it, or responding hospital, or admin
        if (sos.patient == user or
                (sos.responding_hospital and hasattr(user, 'hospital') and
                 sos.responding_hospital.user == user) or
                user.role == 'admin'):
            return sos
        return None

    def get(self, request, pk):
        sos = self._get_sos(request, pk)
        if not sos:
            return error_response('SOS not found.', status_code=404)
        return success_response(data=SOSAlertSerializer(sos).data)


class SOSCancelView(APIView):
    """POST /api/sos/<pk>/cancel/ — patient cancels their SOS."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            sos = SOSAlert.objects.get(pk=pk, patient=request.user)
        except SOSAlert.DoesNotExist:
            return error_response('SOS not found.', status_code=404)
        try:
            sos = cancel_sos(sos, request.user)
        except ValueError as e:
            return error_response(str(e))
        return success_response(data=SOSAlertSerializer(sos).data,
                                message='SOS cancelled.')


class MySOSHistoryView(APIView):
    """GET /api/sos/my/ — patient's SOS history."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = SOSAlert.objects.filter(patient=request.user)
        return success_response(data=SOSAlertSerializer(qs, many=True).data)


# ── Hospital endpoints ────────────────────────────────────────────────────────

class ActiveSOSForHospitalView(APIView):
    """GET /api/sos/hospital/active/ — nearby active SOS list for hospital dashboard."""
    permission_classes = [IsHospitalRole]

    def get(self, request):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital profile not found.', status_code=404)
        if not hospital.latitude or not hospital.longitude:
            return error_response('Hospital location not set.', status_code=400)
        nearby = get_active_sos_for_hospital(hospital)
        results = []
        for sos, dist in nearby:
            d = SOSAlertSerializer(sos).data
            d['distance_km'] = dist
            results.append(d)
        return success_response(data={'count': len(results), 'results': results})


class SOSRespondView(APIView):
    """POST /api/sos/<pk>/respond/ — hospital accepts SOS."""
    permission_classes = [IsHospitalRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital profile not found.', status_code=404)
        try:
            sos = SOSAlert.objects.get(pk=pk)
        except SOSAlert.DoesNotExist:
            return error_response('SOS not found.', status_code=404)
        s = SOSRespondSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        try:
            sos = hospital_accept_sos(
                sos=sos,
                hospital=hospital,
                eta_minutes=s.validated_data['eta_minutes'],
                ambulance_number=s.validated_data.get('ambulance_number', ''),
                changed_by=request.user,
            )
        except ValueError as e:
            return error_response(str(e))
        return success_response(data=SOSAlertSerializer(sos).data,
                                message='SOS accepted. Patient has been notified.')


class SOSEnrouteView(APIView):
    """POST /api/sos/<pk>/enroute/ — hospital marks ambulance as dispatched."""
    permission_classes = [IsHospitalRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(user=request.user)
            sos = SOSAlert.objects.get(pk=pk, responding_hospital=hospital)
        except (Hospital.DoesNotExist, SOSAlert.DoesNotExist):
            return error_response('SOS not found.', status_code=404)
        try:
            sos = hospital_enroute_sos(sos, request.user)
        except ValueError as e:
            return error_response(str(e))
        return success_response(data=SOSAlertSerializer(sos).data,
                                message='Ambulance marked as en route.')


class SOSAmbulanceLocationView(APIView):
    """POST /api/sos/<pk>/location/ — hospital pushes live ambulance GPS."""
    permission_classes = [IsHospitalRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(user=request.user)
            sos = SOSAlert.objects.get(pk=pk, responding_hospital=hospital)
        except (Hospital.DoesNotExist, SOSAlert.DoesNotExist):
            return error_response('SOS not found.', status_code=404)
        s = SOSAmbulanceUpdateSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        sos = update_ambulance_location(
            sos, s.validated_data['ambulance_latitude'],
            s.validated_data['ambulance_longitude'],
        )
        return success_response(data=SOSAlertSerializer(sos).data)


class SOSArrivedView(APIView):
    """POST /api/sos/<pk>/arrived/ — hospital marks ambulance arrived."""
    permission_classes = [IsHospitalRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(user=request.user)
            sos = SOSAlert.objects.get(pk=pk, responding_hospital=hospital)
        except (Hospital.DoesNotExist, SOSAlert.DoesNotExist):
            return error_response('SOS not found.', status_code=404)
        sos = hospital_arrived_sos(sos, request.user)
        return success_response(data=SOSAlertSerializer(sos).data,
                                message='Ambulance marked as arrived.')


class SOSResolveView(APIView):
    """POST /api/sos/<pk>/resolve/ — hospital closes the SOS."""
    permission_classes = [IsHospitalRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(user=request.user)
            sos = SOSAlert.objects.get(pk=pk, responding_hospital=hospital)
        except (Hospital.DoesNotExist, SOSAlert.DoesNotExist):
            return error_response('SOS not found.', status_code=404)
        sos = resolve_sos(sos, request.user)
        return success_response(data=SOSAlertSerializer(sos).data,
                                message='SOS resolved.')