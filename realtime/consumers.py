from notifications.models import Notification
from notifications.utils import send_notification_to_user
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from chat.models import ChatMessages, ChatRooms
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

user = get_user_model()


class GlobalConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4001)  # 4001 : unauthorized
            return

        self.user = self.scope["user"]
        self.user_group_name = f"user_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        # Initialize active rooms tracking
        self.active_rooms = {}

        # Set user as globally online
        await self.set_user_global_online_status(True)

        # Notify all shared rooms that user is online
        await self.notify_shared_rooms_of_user_status("online")

        await self.accept()
        print(f"websocket connect globla consumer User : {self.user.id}")

    async def disconnect(self, close_code):
        # Leave room group
        if not isinstance(self.scope["user"], AnonymousUser):
            # Set user as globally offline
            await self.set_user_global_online_status(False)

            # Notify all shared rooms that user is offline
            await self.notify_shared_rooms_of_user_status("offline")
            # if authorized
            await self.channel_layer.group_discard(
                self.user_group_name, self.channel_name
            )

        # leave all rooms user was in
        if hasattr(self, "active_rooms"):
            for room_id in list(self.active_rooms.keys()):
                room_group_name = f"chat_{room_id}"
                await self.channel_layer.group_discard(
                    room_group_name, self.channel_name
                )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.send(
                text_data=json.dumps({"error": "Unauthorized to send messages."})
            )
            await self.close(code=4001)
            return

        try:

            text_data_json = json.loads(text_data)

            message_type = text_data_json.get("type")

            if message_type == "join_room":
                await self.handle_join_room(text_data_json)
            elif message_type == "leave_room":
                await self.handle_leave_room(text_data_json)
            elif message_type == "send_message":
                # todo add this method
                await self.handle_send_message(text_data_json)

            elif message_type == "typing":
                # todo add this method
                await self.handle_typing_indicator(text_data_json)

            else:
                await self.send(
                    text_data=json.dumps(
                        {"error": f"Unknown message type: {message_type}"}
                    )
                )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON  format"}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Server error: {str(e)}"}))

    # Receive message from room group (event Handler for message)
    async def chat_message(self, event):
        # Send message object directly to WebSocket
        await self.send(
            text_data=json.dumps({
                "type": "chat_message", "message": event["message"]},ensure_ascii=False
)
        )

    # handler for room join message
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
                    # add the user infos here
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

    # event Handler for typing indicator event (resived from the room group)

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

    # -- HELPER METHODS FOR DB OPERATIONS --

    # todo : move those funcs to chat.services.py
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
                    "users": event["users"],  # This will be the list of user dicts
                }
            )
        )

    # HANDLER FOR EDITED MESSAGES
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

    # HANDLER FOR DELETED MESSAGES
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

    # --- HELPER METHODS FOR REDIS PRESENCE TRACKING  ---

    def get_presence_key(self, room_id):
        """Generates the Redis key for a room's presence set."""
        return f"room:{room_id}:presence"

    async def add_user_to_redis_presence(self, room_id, user_id):
        """Adds a user's ID to the Redis Set for room presence."""
        await self.channel_layer.connection(0).sadd(
            self.get_presence_key(room_id), user_id
        )

    async def remove_user_from_redis_presence(self, room_id, user_id):
        """Removes a user's ID from the Redis Set for room presence."""
        await self.channel_layer.connection(0).srem(
            self.get_presence_key(room_id), user_id
        )

    async def get_users_from_redis_presence(self, room_id):
        """Retrieves all user IDs from the Redis Set for room presence."""
        user_ids_bytes = await self.channel_layer.connection(0).smembers(
            self.get_presence_key(room_id)
        )
        return [uid.decode("utf-8") for uid in user_ids_bytes]

    @database_sync_to_async
    def get_user_data_for_presence_list(self, user_ids):
        """Fetches full name and ID for a list of user IDs from the database."""
        if not user_ids:
            return []

        users = user.objects.filter(id__in=user_ids).values("id", "full_name")
        return [
            {"id": str(user["id"]), "full_name": user["full_name"]} for user in users
        ]

    async def set_user_global_online_status(self, is_online):
        """Set user's global online status in Redis"""
        status = "online" if is_online else "offline"
        await self.channel_layer.connection(0).hset(
            "global_user_status", str(self.user.id), status
        )

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

    async def notify_shared_rooms_of_user_status(self, status):
        """Notify all rooms this user is a member of about their status"""
        # Get all rooms this user is a member of
        user_rooms = await self.get_user_all_rooms()
        for room_id in user_rooms:
            room_group_name = f"chat_{room_id}"
            await self.channel_layer.group_send(
                room_group_name,
                {
                    "type": "user.status.changed",
                    "user_id": str(self.user.id),
                    "full_name": self.user.full_name,
                    "status": status,  # "online" or "offline"
                },
            )

    async def user_status_changed(self, event):
        """Handle user status change events"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_status_changed",
                    "user_id": event["user_id"],
                    "full_name": event["full_name"],
                    "status": event["status"],  # "online" or "offline"
                }
            )
        )

    # ROOM LIST UPDATE METHODS

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

    @database_sync_to_async
    def get_all_room_member_ids(self, room_obj):
        try:
            member_ids = room_obj.members.values_list("user_id_id", flat=True)
            return [str(mid) for mid in member_ids]
        except Exception as e:
            return []
        
        

    #notification event handler
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

    @database_sync_to_async
    def create_notification(self, user_id, sender_name, room_name, message_content, room_id):
        """Create notification in database"""
        from notifications.models import Notification
        from django.contrib.auth import get_user_model
        
        try:
            User = get_user_model()
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




