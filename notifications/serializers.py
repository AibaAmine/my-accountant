from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieving notifications"""

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "related_object_id",
            "created_at",
        ]
        read_only_fields = ["notification_id", "created_at"]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification (mark as read)"""

    class Meta:
        model = Notification
        fields = ["is_read"]


class UnreadCountSerializer(serializers.Serializer):
    """Serializer for unread count response"""

    unread_count = serializers.IntegerField()
