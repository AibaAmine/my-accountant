from channels.db import database_sync_to_async
from datetime import datetime
from chat.models import ChatMessages, ChatRooms
from django.contrib.auth import get_user_model

User = get_user_model()


class DatabaseOperations:
    """Mixin class containing all database operations"""

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRooms.objects.get(room_id=room_id)
        except ChatRooms.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_member_of_room(self, room, user):
        # Always check membership regardless of room type
        return room.members.filter(user_id=user).exists()

    @database_sync_to_async
    def save_chat_message(self, room, sender, content):
        try:
            created_msg = ChatMessages.objects.create(
                room=room, sender=sender, content=content, edited_at=datetime.now()
            )
            print(f"Saved message from {sender.id} to room {room.room_name}")
            return created_msg
        except Exception as e:
            print(f"Error saving chat message : {e}")
            return None

    @database_sync_to_async
    def get_user_data_for_presence_list(self, user_ids):
        """Fetches full name and ID for a list of user IDs from the database."""
        if not user_ids:
            return []

        users = User.objects.filter(id__in=user_ids).values("id", "full_name")
        return [
            {"id": str(user["id"]), "full_name": user["full_name"]} for user in users
        ]

    @database_sync_to_async
    def get_user_all_rooms(self):
        """Get all room IDs this user is a member of"""
        try:
            from chat.models import ChatMembers

            room_ids = ChatMembers.objects.filter(user_id=self.user).values_list(
                "room_id__room_id", flat=True
            )
            return [str(room_id) for room_id in room_ids]
        except Exception as e:
            print(f"Error getting user rooms: {e}")
        return []

    @database_sync_to_async
    def get_all_room_member_ids(self, room_obj):
        try:
            member_ids = room_obj.members.values_list("user_id_id", flat=True)
            return [str(mid) for mid in member_ids]
        except Exception as e:
            return []

    @database_sync_to_async
    def create_notification(self, user_id, sender_name, room_name, message_content, room_id):
        """Create notification in database"""
        from notifications.models import Notification
        
        try:
            user = User.objects.get(id=user_id)
            
            # Truncate message if too long
            preview = message_content[:50] + "..." if len(message_content) > 50 else message_content
            
            notification = Notification.objects.create(
                user=user,
                notification_type="message",
                title=f"New message from {sender_name}",
                message=f"{sender_name} in {room_name}: {preview}",
                related_object_id=room_id,
            )
            return notification
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
    
    @database_sync_to_async
    def send_notification_sync(self, notification):
        """Send notification via WebSocket (sync wrapper)"""
        from notifications.utils import send_notification_to_user
        send_notification_to_user(notification)