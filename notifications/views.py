from .serializers import NotificationSerializer, NotificationUpdateSerializer
from .models import Notification
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadAPIView(generics.UpdateAPIView):
    lookup_field = "notification_id"
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationUpdateSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)

    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        if instance.is_read:
            return Response(
                {
                    "notification_id": str(instance.notification_id),
                    "is_read": True,
                    "message": "Notification was already marked as read",
                }
            )

        serializer = self.get_serializer(instance, data={"is_read": True}, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "notification_id": str(instance.notification_id),
                "is_read": True,
                "message": "Notification marked as read successfully",
            }
        )


class NotificationUnreadCountAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = self.request.user

        unread_count = Notification.objects.filter(user=user, is_read=False).count()

        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)



class MarkAllAsRead(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        unread_notification = Notification.objects.filter(
            user=self.request.user, is_read=False
        )

        marked_count = unread_notification.count()

        unread_notification.update(is_read=True)

        new_unread_count = Notification.objects.filter(
            user=self.request.user, is_read=False
        ).count()

        return Response(
            {
                "message": f"{marked_count} notification marked as read",
                "marked_count": marked_count,
                "unread_count": new_unread_count,
            },
            status=status.HTTP_200_OK,
        )

