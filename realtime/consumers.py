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

        await self.accept()
        print(f"websocket connect globla consumer User : {self.user.id}")

    async def disconnect(self, close_code):
        # Leave room group
        if not isinstance(self.scope["user"], AnonymousUser):
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
                # todo add this method
                await self.handle_join_room(text_data_json)
            elif message_type == "leave_room":
                # todo add this method
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
            text_data=json.dumps({"type": "chat_message", "message": event["message"]})
        )

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

    # -- HELPER METHODS FOR DB OPERATIONS --

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

    # --- Handlers for user join/leave/list events (called by channel layer) ---
    async def user_join(self, event):
        """
        Handles 'user.join' events received from the channel layer.
        This event is broadcast when a user connects to the room.
        It sends a 'user_join' message to the WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_join",
                    "user_id": event["user_id"],
                    "full_name": event["full_name"],
                }
            )
        )

    async def user_leave(self, event):
        """
        Handles 'user.leave' events received from the channel layer.
        This event is broadcast when a user disconnects from the room.
        It sends a 'user_leave' message to the WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_leave",
                    "user_id": event["user_id"],
                    "user_full_name": event["full_name"],
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
