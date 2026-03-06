from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification, FCMToken
from .serializers import NotificationSerializer, FCMTokenSerializer
from utils.response import success_response, error_response

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)
        unread = qs.filter(is_read=False).count()
        return success_response(data={'unread': unread, 'results': NotificationSerializer(qs[:50], many=True).data})

class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk=None):
        qs = Notification.objects.filter(recipient=request.user)
        if pk:
            qs = qs.filter(pk=pk)
        qs.update(is_read=True)
        return success_response(message='Marked as read.')

class FCMTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        s = FCMTokenSerializer(data=request.data)
        if not s.is_valid(): return error_response('Validation failed.', s.errors)
        FCMToken.objects.update_or_create(
            user=request.user, token=s.validated_data['token'],
            defaults={'device': s.validated_data.get('device','')}
        )
        return success_response(message='FCM token registered.')
    def delete(self, request):
        token = request.data.get('token')
        if token:
            FCMToken.objects.filter(user=request.user, token=token).delete()
        return success_response(message='FCM token removed.')