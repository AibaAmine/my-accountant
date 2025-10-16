import json
from channels.db import database_sync_to_async
from datetime import datetime
from chat.models import ChatMessages, ChatRooms
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatHandlers:
    """Mixin class containing all chat-related handler methods"""

    async def handle_join_room(self, data):
        room_id = data.get("room_id")
        if not room_id:
            await self.send(text_data=json.dumps({"error": "room_id is required"}))
            return

        room_obj = await self.get_room(room_id)
        if not room_obj:
            await self.send(text_data=json.dumps({"error": "Room not found"}))
            return

        if not await self.is_user_member_of_room(room_obj, self.user):
            await self.send(
                text_data=json.dumps({"error": "Not authorized to join this room"})
            )
            return

        # join room group
        room_group_name = f"chat_{room_id}"
        await self.channel_layer.group_add(room_group_name, self.channel_name)

        self.active_rooms[room_id] = room_obj

        # Send success response
        await self.send(
            text_data=json.dumps(
                {
                    "type": "room_joined",
                    "room_id": room_id,
                    "room_name": room_obj.room_name,
                }
            )
        )

    async def handle_typing_indicator(self, data):
        room_id = data.get("room_id")
        is_typing = data.get("is_typing", False)

        if not room_id:
            await self.send(text_data=json.dumps({"error": "room_id is required"}))
            return

        # Check if user is in the room
        if room_id not in self.active_rooms:
            await self.send(
                text_data=json.dumps({"error": "You must join the room first"})
            )
            return

        room_obj = self.active_rooms[room_id]
        room_group_name = f"chat_{room_id}"

        # Broadcast typing indicator to others in room
        await self.channel_layer.group_send(
            room_group_name,
            {
                "type": "typing.indicator",
                "user": self.user.full_name,
                "user_id": str(self.user.id),
                "is_typing": is_typing,
                "room": room_obj.room_name,
                "room_id": room_id,
            },
        )

    async def handle_leave_room(self, data):
        room_id = data.get("room_id")
        if not room_id:
            await self.send(text_data=json.dumps({"error": "room_id is required"}))
            return

        if room_id not in self.active_rooms:
            await self.send(text_data=json.dumps({"error": "You are not in this room"}))
            return

        room_obj = self.active_rooms[room_id]
        room_group_name = f"chat_{room_id}"

        await self.channel_layer.group_discard(room_group_name, self.channel_name)

        del self.active_rooms[room_id]

        await self.send(text_data=json.dumps({"type": "room_left", "room_id": room_id}))

    async def handle_send_message(self, data):
        room_id = data.get("room_id")
        content = data.get("content")
        if not room_id or not content:
            await self.send(
                text_data=json.dumps({"error": "room_id and content are required"})
            )
            return

        if room_id not in self.active_rooms:
            await self.send(
                text_data=json.dumps({"error": "You must join the room first"})
            )
            return

        room_obj = self.active_rooms[room_id]

        try:
            # Save message to database
            created_msg = await self.save_chat_message(room_obj, self.user, content)
            if not created_msg:
                await self.send(
                    text_data=json.dumps({"error": "Failed to save message"})
                )
                return

            # Broadcast message to all room members (including sender)
            room_group_name = f"chat_{room_id}"
            await self.channel_layer.group_send(
                room_group_name,
                {
                    "type": "chat_message",
                    "message": {
                        "message_id": str(created_msg.message_id),
                        "content": created_msg.content,
                        "sender": {
                            "id": str(created_msg.sender.id),
                            "full_name": created_msg.sender.full_name,
                        },
                        "sent_at": created_msg.sent_at.isoformat(),
                        "edited_at": (
                            created_msg.edited_at.isoformat()
                            if created_msg.edited_at
                            else None
                        ),
                        "is_deleted": False,
                        "is_edited": created_msg.is_edited,
                        "message_type": created_msg.message_type,
                        "file": str(created_msg.file) if created_msg.file else None,
                        "room_id": room_id,
                    },
                },
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "message_sent",
                        "message_id": str(created_msg.message_id),
                        "room_id": room_id,
                        "status": "delivered",
                    }
                )
            )

            # Send room list update to ALL room members
            await self.send_room_list_update_to_members(room_obj, created_msg)
            
            await self.create_message_notifications(room_obj, created_msg)

        except Exception as e:
            print(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({"error": f"Server error: {e}"}))
            return

    async def send_room_list_update_to_members(self, room_obj, message):
        try:
            room_members = await self.get_all_room_member_ids(room_obj)

            for user_id in room_members:
                # Check if user has unread messages (anyone except the sender)
                has_unread = str(user_id) != str(message.sender.id)

                user_group_name = f"user_{user_id}"
                await self.channel_layer.group_send(
                    user_group_name,
                    {
                        "type": "room.list.update",
                        "room_id": str(room_obj.room_id),
                        "room_name": room_obj.room_name,
                        "is_dm": room_obj.is_dm,
                        "has_unread": has_unread,
                        "latest_message": {
                            "message_id": str(message.message_id),
                            "content": message.content,
                            "sender": {
                                "id": str(message.sender.id),
                                "full_name": message.sender.full_name,
                            },
                            "sent_at": message.sent_at.isoformat(),
                            "edited_at": (
                                message.edited_at.isoformat()
                                if message.edited_at
                                else None
                            ),
                            "is_deleted": message.is_deleted,
                            "is_edited": message.is_edited,
                            "message_type": message.message_type,
                            "file": str(message.file) if message.file else None,
                        },
                    },
                )

        except Exception as e:
            print(f"Error sending room list updates: {e}")
            return

    async def create_message_notifications(self, room_obj, message):
        """Create message notifications for all room members except sender"""
        
        try:
            room_members = await self.get_all_room_member_ids(room_obj)
            
            for user_id in room_members:
                if str(user_id) == str(message.sender.id):
                    continue
                
                # Create notification for this user
                notification = await self.create_notification(
                    user_id=user_id,
                    sender_name=message.sender.full_name,
                    room_name=room_obj.room_name,
                    message_content=message.content,
                    room_id=str(room_obj.room_id)
                )
                
                if notification:
                    print("there is notification created when sending msg")
                    await self.send_notification_sync(notification)
                    
        except Exception as e:
            print(f"Error creating message notifications: {e}")