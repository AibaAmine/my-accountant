from notifications.models import Notification
from notifications.utils import send_notification_to_user
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from chat.models import ChatMessages, ChatRooms
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .chat_handlers import ChatHandlers
from .event_handlers import EventHandlers
from .db import DatabaseOperations

user = get_user_model()


class GlobalConsumer(AsyncWebsocketConsumer, ChatHandlers, EventHandlers, DatabaseOperations):

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
                await self.handle_send_message(text_data_json)
            elif message_type == "typing":
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

    async def set_user_global_online_status(self, is_online):
        """Set user's global online status in Redis"""
        status = "online" if is_online else "offline"
        await self.channel_layer.connection(0).hset(
            "global_user_status", str(self.user.id), status
        )

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