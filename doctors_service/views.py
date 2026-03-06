import datetime
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import DoctorProfile, WeeklySchedule, SlotBlock, TimeSlot, DoctorReview
from .serializers import (DoctorListSerializer, DoctorDetailSerializer,
    DoctorProfileWriteSerializer, WeeklyScheduleSerializer,
    SlotBlockSerializer, TimeSlotSerializer, DoctorReviewSerializer)
from .doctor_service import search_doctors, get_available_slots
from utils.response import success_response, error_response
from utils.permission import IsDoctorRole


class DoctorListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        qs   = search_doctors(
            query         = request.query_params.get('q',''),
            specialization= request.query_params.get('specialization',''),
            city          = request.query_params.get('city',''),
            available_only= request.query_params.get('available','').lower()=='true',
        )
        return success_response(data={'count':qs.count(),'results':DoctorListSerializer(qs,many=True).data})


class DoctorDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            doc = DoctorProfile.objects.select_related('user','hospital').get(pk=pk)
        except DoctorProfile.DoesNotExist:
            return error_response('Doctor not found.', status_code=404)
        return success_response(data=DoctorDetailSerializer(doc).data)


class DoctorAvailableSlotsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            doc = DoctorProfile.objects.get(pk=pk)
        except DoctorProfile.DoesNotExist:
            return error_response('Doctor not found.', status_code=404)
        date_str = request.query_params.get('date', str(datetime.date.today()))
        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return error_response('Invalid date format. Use YYYY-MM-DD.')
        slots = get_available_slots(doc, date)
        return success_response(data=TimeSlotSerializer(slots, many=True).data)


class MyDoctorProfileView(APIView):
    permission_classes = [IsDoctorRole]
    def _profile(self, user):
        try:
            return DoctorProfile.objects.get(user=user)
        except DoctorProfile.DoesNotExist:
            return None

    def get(self, request):
        p = self._profile(request.user)
        if not p:
            return error_response('Profile not found.', status_code=404)
        return success_response(data=DoctorDetailSerializer(p).data)

    def post(self, request):
        if self._profile(request.user):
            return error_response('Profile already exists. Use PUT.')
        s = DoctorProfileWriteSerializer(data=request.data)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        p = s.save(user=request.user)
        return success_response(data=DoctorDetailSerializer(p).data, message='Profile created.', status_code=201)

    def put(self, request):
        p = self._profile(request.user)
        if not p:
            return error_response('Profile not found.', status_code=404)
        s = DoctorProfileWriteSerializer(p, data=request.data, partial=True)
        if not s.is_valid():
            return error_response('Validation failed.', s.errors)
        return success_response(data=DoctorDetailSerializer(s.save()).data, message='Profile updated.')


class MyWeeklyScheduleView(APIView):
    permission_classes = [IsDoctorRole]
    def _doc(self, user):
        try: return DoctorProfile.objects.get(user=user)
        except: return None

    def get(self, request):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        return success_response(data=WeeklyScheduleSerializer(doc.weekly_schedule.all(), many=True).data)

    def post(self, request):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        s = WeeklyScheduleSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        obj = s.save(doctor=doc)
        return success_response(data=WeeklyScheduleSerializer(obj).data, status_code=201)

    def put(self, request, day):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        try:
            sched = WeeklySchedule.objects.get(doctor=doc, day_of_week=day)
        except WeeklySchedule.DoesNotExist:
            return error_response('Schedule not found.', status_code=404)
        s = WeeklyScheduleSerializer(sched, data=request.data, partial=True)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        return success_response(data=WeeklyScheduleSerializer(s.save()).data)

    def delete(self, request, day):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        try:
            WeeklySchedule.objects.get(doctor=doc, day_of_week=day).delete()
        except WeeklySchedule.DoesNotExist:
            return error_response('Schedule not found.', status_code=404)
        return success_response(message='Schedule removed.')


class SlotBlockView(APIView):
    permission_classes = [IsDoctorRole]
    def _doc(self, user):
        try: return DoctorProfile.objects.get(user=user)
        except: return None

    def get(self, request):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        return success_response(data=SlotBlockSerializer(doc.slot_blocks.all(), many=True).data)

    def post(self, request):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        s = SlotBlockSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        return success_response(data=SlotBlockSerializer(s.save(doctor=doc)).data, status_code=201)

    def delete(self, request, block_id):
        doc = self._doc(request.user)
        if not doc: return error_response('Profile not found.', status_code=404)
        try:
            SlotBlock.objects.get(pk=block_id, doctor=doc).delete()
        except SlotBlock.DoesNotExist:
            return error_response('Block not found.', status_code=404)
        return success_response(message='Block removed.')


class DoctorReviewView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET': return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        try: doc = DoctorProfile.objects.get(pk=pk)
        except DoctorProfile.DoesNotExist: return error_response('Doctor not found.', status_code=404)
        reviews = DoctorReview.objects.filter(doctor=doc).order_by('-created_at')
        return success_response(data=DoctorReviewSerializer(reviews, many=True).data)

    def post(self, request, pk):
        try: doc = DoctorProfile.objects.get(pk=pk)
        except DoctorProfile.DoesNotExist: return error_response('Doctor not found.', status_code=404)
        if DoctorReview.objects.filter(doctor=doc, patient=request.user).exists():
            return error_response('You have already reviewed this doctor.')
        s = DoctorReviewSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        review = s.save(doctor=doc, patient=request.user)
        return success_response(data=DoctorReviewSerializer(review).data, status_code=201)