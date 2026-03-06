from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Hospital, Department, Amenity, CapacityLog
from .serializers import (
    HospitalListSerializer, HospitalDetailSerializer,
    HospitalWriteSerializer, CapacityUpdateSerializer,
    CapacityLogSerializer, DepartmentSerializer, AmenitySerializer,
)
from .hospital_service import get_nearby_hospitals, search_hospitals, update_capacity
from utils.response import success_response, error_response
from utils.permission import IsHospitalRole, IsAdminRole, IsHospitalOrAdmin


# ── Public ────────────────────────────────────────────────────────────────────

class HospitalListView(APIView):
    """GET /api/hospitals/?q=&city=&department=&has_icu=true"""
    permission_classes = [AllowAny]

    def get(self, request):
        qs = search_hospitals(
            query=request.query_params.get('q', ''),
            city=request.query_params.get('city', ''),
            department=request.query_params.get('department', ''),
            has_icu=request.query_params.get('has_icu', '').lower() == 'true',
        )
        data = HospitalListSerializer(qs, many=True).data
        return success_response(data={'count': qs.count(), 'results': data})


class HospitalDetailView(APIView):
    """GET /api/hospitals/<pk>/"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            hospital = Hospital.objects.get(pk=pk, status=Hospital.Status.ACTIVE)
        except Hospital.DoesNotExist:
            return error_response('Hospital not found.', status_code=404)
        return success_response(data=HospitalDetailSerializer(hospital).data)


class NearbyHospitalsView(APIView):
    """GET /api/hospitals/nearby/?lat=&lon=&radius="""
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        if not lat or not lon:
            return error_response('lat and lon are required.')
        try:
            lat, lon = float(lat), float(lon)
        except ValueError:
            return error_response('lat and lon must be numbers.')
        radius    = float(request.query_params.get('radius', 20))
        hospitals = get_nearby_hospitals(lat, lon, radius_km=radius)
        data      = HospitalListSerializer(hospitals, many=True).data
        return success_response(data={'count': len(hospitals), 'results': data})


# ── Hospital user — own profile ───────────────────────────────────────────────

class MyHospitalView(APIView):
    """Hospital user manages their own Hospital record."""
    permission_classes = [IsHospitalRole]

    def _get_hospital(self, user):
        try:
            return Hospital.objects.get(user=user)
        except Hospital.DoesNotExist:
            return None

    def get(self, request):
        hospital = self._get_hospital(request.user)
        if not hospital:
            return error_response('Hospital profile not found.', status_code=404)
        return success_response(data=HospitalDetailSerializer(hospital).data)

    def post(self, request):
        if self._get_hospital(request.user):
            return error_response('Hospital profile already exists. Use PUT to update.')
        serializer = HospitalWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        hospital = serializer.save(user=request.user)
        return success_response(
            data=HospitalDetailSerializer(hospital).data,
            message='Hospital profile created.',
            status_code=201,
        )

    def put(self, request):
        hospital = self._get_hospital(request.user)
        if not hospital:
            return error_response('Hospital profile not found.', status_code=404)
        serializer = HospitalWriteSerializer(hospital, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        hospital = serializer.save()
        return success_response(
            data=HospitalDetailSerializer(hospital).data,
            message='Hospital profile updated.',
        )


class CapacityUpdateView(APIView):
    """POST /api/hospitals/my/capacity/"""
    permission_classes = [IsHospitalRole]

    def post(self, request):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital profile not found.', status_code=404)
        serializer = CapacityUpdateSerializer(data=request.data, context={'hospital': hospital})
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        hospital = update_capacity(
            hospital=hospital,
            available_beds=serializer.validated_data['available_beds'],
            icu_available=serializer.validated_data['icu_available'],
            emergency_available=serializer.validated_data['emergency_available'],
        )
        return success_response(
            data=HospitalDetailSerializer(hospital).data,
            message='Capacity updated successfully.',
        )


class CapacityLogView(APIView):
    """GET /api/hospitals/my/capacity/logs/"""
    permission_classes = [IsHospitalRole]

    def get(self, request):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital not found.', status_code=404)
        logs = CapacityLog.objects.filter(hospital=hospital)[:50]
        return success_response(data=CapacityLogSerializer(logs, many=True).data)


class DepartmentView(APIView):
    """GET + POST /api/hospitals/my/departments/"""
    permission_classes = [IsHospitalRole]

    def get(self, request):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital not found.', status_code=404)
        data = DepartmentSerializer(hospital.departments.all(), many=True).data
        return success_response(data=data)

    def post(self, request):
        try:
            hospital = Hospital.objects.get(user=request.user)
        except Hospital.DoesNotExist:
            return error_response('Hospital not found.', status_code=404)
        serializer = DepartmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        dept = serializer.save(hospital=hospital)
        return success_response(data=DepartmentSerializer(dept).data, status_code=201)


class DepartmentDetailView(APIView):
    """PUT + DELETE /api/hospitals/my/departments/<dept_id>/"""
    permission_classes = [IsHospitalRole]

    def _get(self, user, dept_id):
        try:
            hospital = Hospital.objects.get(user=user)
            return Department.objects.get(pk=dept_id, hospital=hospital)
        except (Hospital.DoesNotExist, Department.DoesNotExist):
            return None

    def put(self, request, dept_id):
        dept = self._get(request.user, dept_id)
        if not dept:
            return error_response('Department not found.', status_code=404)
        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response('Validation failed.', serializer.errors)
        return success_response(data=DepartmentSerializer(serializer.save()).data)

    def delete(self, request, dept_id):
        dept = self._get(request.user, dept_id)
        if not dept:
            return error_response('Department not found.', status_code=404)
        dept.delete()
        return success_response(message='Department removed.')


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminHospitalListView(APIView):
    """GET /api/hospitals/admin/all/"""
    permission_classes = [IsAdminRole]

    def get(self, request):
        qs   = Hospital.objects.all()
        data = HospitalListSerializer(qs, many=True).data
        return success_response(data={'count': qs.count(), 'results': data})


class AdminVerifyHospitalView(APIView):
    """POST /api/hospitals/admin/<pk>/verify/"""
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            hospital = Hospital.objects.get(pk=pk)
        except Hospital.DoesNotExist:
            return error_response('Hospital not found.', status_code=404)
        hospital.is_verified = not hospital.is_verified
        hospital.save(update_fields=['is_verified'])
        label = 'verified' if hospital.is_verified else 'unverified'
        return success_response(message=f'Hospital {label} successfully.')