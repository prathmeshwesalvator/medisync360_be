from rest_framework import serializers
from .models import Notification, FCMToken

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id','title','body','notif_type','data','is_read','fcm_sent','created_at']

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FCMToken
        fields = ['id','token','device','created_at']