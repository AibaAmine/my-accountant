from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification_to_user(notification):
    
    channel_layer = get_channel_layer()
    user_group_name = f"user_{notification.user.id}"
    
    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            "type": "new.notification",
            "notification_id": str(notification.notification_id),
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "related_object_id": str(notification.related_object_id) if notification.related_object_id else None,
            "created_at": notification.created_at.isoformat(),
            "is_read": notification.is_read,
        }
    )