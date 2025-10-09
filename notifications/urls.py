from django.urls import path
from . import views

urlpatterns = [
    path("", views.NotificationListAPIView.as_view(), name="notification-list"),
    path(
        "<uuid:notification_id>/mark-read/",
        views.NotificationMarkReadAPIView.as_view(),
        name="notification-mark-read",
    ),
    path(
        "unread-count/",
        views.NotificationUnreadCountAPIView.as_view(),
        name="notification-unread-count",
    ),
    path(
        "mark-all-read/",
        views.MarkAllAsRead.as_view(),
        name="mark-all-notifications-read",
    ),
]
