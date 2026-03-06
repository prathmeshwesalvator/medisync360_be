from django.urls import path
from .views import NotificationListView, MarkReadView, FCMTokenView

urlpatterns = [
    path('',               NotificationListView.as_view(), name='notification-list'),
    path('read/',          MarkReadView.as_view(),          name='mark-all-read'),
    path('<int:pk>/read/', MarkReadView.as_view(),          name='mark-read'),
    path('fcm/',           FCMTokenView.as_view(),          name='fcm-token'),
]