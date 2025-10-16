import json


class EventHandlers:
    """Mixin class containing all WebSocket event handlers"""

    async def chat_message(self, event):
        # Send message object directly to WebSocket
        await self.send(
            text_data=json.dumps({
                "type": "chat_message", "message": event["message"]}, ensure_ascii=False)
        )

    async def typing_indicator(self, event):
        user = event["user"]
        room = event["room"]
        user_id = event["user_id"]
        is_typing = event["is_typing"]

        if user_id == str(self.scope["user"].id):
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing_indicator",
                    "user": user,
                    "user_id": user_id,
                    "room": room,
                    "is_typing": is_typing,
                }
            )
        )

    async def member_added(self, event):
        """Handle new member added to room"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "member_added",
                    "user_id": event["user_id"],
                    "full_name": event["full_name"],
                    "room_id": event["room_id"],
                    "added_by": event["added_by"],
                    "added_by_name": event["added_by_name"],
                }
            )
        )

    async def member_removed(self, event):
        """Handle member removed from room"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "member_removed",
                    "user_id": event["user_id"],
                    "full_name": event["full_name"],
                    "room_id": event["room_id"],
                    "removed_by": event["removed_by"],
                    "removed_by_name": event["removed_by_name"],
                }
            )
        )

    async def room_users_list(self, event):
        """
        Handles 'room_users_list' events received from the channel layer.
        This event is sent to a newly connecting client with the initial list of users.
        It sends a 'room_users_list' message to the WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "room_users_list",
                    "users": event["users"],
                }
            )
        )

    async def message_edited(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message_edited",
                    "message_id": event["message_id"],
                    "new_content": event["new_content"],
                    "edited_at": event["edited_at"],
                    "room_id": event["room_id"],
                    "sender_id": event["sender_id"],
                    "sender_full_name": event["sender_full_name"],
                }
            )
        )

    async def message_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message_deleted",
                    "message_id": event["message_id"],
                    "room_id": event["room_id"],
                    "edited_at": event["edited_at"],
                }
            )
        )

    async def user_status_changed(self, event):
        """Handle user status change events"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_status_changed",
                    "user_id": event["user_id"],
                    "full_name": event["full_name"],
                    "status": event["status"],
                }
            )
        )

    async def room_list_update(self, event):
        """Handle room list update events"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "room_list_update",
                    "room_id": event["room_id"],
                    "room_name": event["room_name"],
                    "is_dm": event["is_dm"],
                    "has_unread": event["has_unread"],
                    "latest_message": event["latest_message"],
                }
            )
        )

    async def new_notification(self, event):
        """Handle new notification events"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_notification",
                    "notification_id": event["notification_id"],
                    "notification_type": event["notification_type"],
                    "title": event["title"],
                    "message": event["message"],
                    "related_object_id": event["related_object_id"],
                    "created_at": event["created_at"],
                    "is_read": event["is_read"],
                },
                ensure_ascii=False
            )
        )