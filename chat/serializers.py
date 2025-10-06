from .models import ChatMessages, ChatRooms
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
from accounts.serializers import CustomUserDetailsSerializer

User = get_user_model()


class DirectMessageRoomSerializer(serializers.ModelSerializer):
    """Specialized serializer for DM rooms showing the other user and latest message"""

    other_user = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()
    has_unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRooms
        fields = [
            "room_id",
            "other_user",
            "latest_message",
            "has_unread_messages",
            "created_at",
        ]
        read_only_fields = fields

    def get_other_user(self, obj):
        """Get the other user in the DM (not the current user)"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        current_user = request.user

        # Get the other member in the DM room
        other_member = obj.members.exclude(user_id=current_user).first()
        if other_member:
            return CustomUserDetailsSerializer(
                other_member.user_id, context=self.context
            ).data

        return None

    def get_latest_message(self, obj):
        """Get the most recent message in the room"""
        latest_msg = obj.messages.order_by("-sent_at").first()
        if latest_msg:
            return {
                "message_id": str(latest_msg.message_id),
                "content": latest_msg.content,
                "message_type": latest_msg.message_type,
                "file": latest_msg.file.url if latest_msg.file else None,
                "sent_at": latest_msg.sent_at,
                "is_deleted": latest_msg.is_deleted,
                "is_edited": latest_msg.is_edited,
                "edited_at": latest_msg.edited_at,
                "sender": CustomUserDetailsSerializer(
                    latest_msg.sender, context=self.context
                ).data,
            }
        return None

    def get_has_unread_messages(self, obj):
        """Returns True if room has unread messages for the requesting user"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        user_last_seen_records = getattr(obj, "prefetched_user_last_seen", None)

        if user_last_seen_records is not None:
            if user_last_seen_records:
                last_seen_time = user_last_seen_records[0].last_seen_at
            else:
                # Never seen this room = has unread messages if any messages exist
                return obj.messages.filter(is_deleted=False).exists()
        else:
            # Fallback to database query
            try:
                last_seen = obj.user_last_seen.get(user=user)
                last_seen_time = last_seen.last_seen_at
            except obj.user_last_seen.model.DoesNotExist:
                return obj.messages.filter(is_deleted=False).exists()

        # Check if there are messages after last seen time (excluding user's own messages)
        return (
            obj.messages.filter(sent_at__gt=last_seen_time, is_deleted=False)
            .exclude(sender=user)
            .exists()
        )


class ChatRoomSerializer(serializers.ModelSerializer):
    creator = CustomUserDetailsSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()
    # boolean to check if the room has unread messages
    has_unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRooms
        fields = [
            "room_id",
            "creator",
            "room_name",
            "created_at",
            "description",
            "is_private",
            "is_dm",
            "members_count",
            "message_count",
            "latest_message",
            "has_unread_messages",
        ]
        read_only_fields = [
            "room_id",
            "creator",
            "created_at",
            "is_private",
            "is_dm",
            "members_count",
            "message_count",
            "latest_message",
            "has_unread_messages",
        ]

    def get_message_count(self, obj):
        return getattr(obj, "message_count_annotated", obj.messages.count())

    def get_members_count(self, obj):
        return getattr(obj, "members_count_annotated", obj.members.count())

    def get_latest_message(self, obj):
        """Get the most recent message in the room"""
        latest_msg = obj.messages.order_by("-sent_at").first()
        if latest_msg:
            return {
                "message_id": str(latest_msg.message_id),
                "content": latest_msg.content,
                "message_type": latest_msg.message_type,
                "file": latest_msg.file.url if latest_msg.file else None,
                "sent_at": latest_msg.sent_at,
                "is_deleted": latest_msg.is_deleted,
                "is_edited": latest_msg.is_edited,
                "edited_at": latest_msg.edited_at,
                "sender": CustomUserDetailsSerializer(
                    latest_msg.sender, context=self.context
                ).data,
            }
        return None

    def get_has_unread_messages(self, obj):
        """Returns True if room has unread messages for the requesting user"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        user_last_seen_records = getattr(obj, "prefetched_user_last_seen", None)

        if user_last_seen_records is not None:
            # We have prefetched data
            if user_last_seen_records:
                last_seen_time = user_last_seen_records[0].last_seen_at
            else:
                # Never seen this room = has unread messages if any messages exist
                return obj.messages.exists()
        else:
            # Fallback to database query
            try:
                last_seen = obj.user_last_seen.get(user=user)  # Use your related_name
                last_seen_time = last_seen.last_seen_at
            except obj.user_last_seen.model.DoesNotExist:
                return obj.messages.exists()

        # Check if there are messages after last seen time (excluding user's own messages)
        return (
            obj.messages.filter(sent_at__gt=last_seen_time, is_deleted=False)
            .exclude(sender=user)
            .exists()
        )


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRooms
        fields = ["room_id", "room_name", "description", "is_private"]
        read_only_fields = ["room_id", "created_at", "creator", "is_dm"]


class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRooms
        fields = ["room_name", "description", "is_private"]
        read_only_fields = ["room_id", "created_at", "creator", "is_dm"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = CustomUserDetailsSerializer(read_only=True)
    room = ChatRoomSerializer(read_only=True)
    timestamp = serializers.DateTimeField(source="sent_at", read_only=True)

    class Meta:
        model = ChatMessages
        fields = [
            "message_id",
            "room",
            "sender",
            "content",
            "timestamp",
            "edited_at",
            "is_deleted",
        ]
        read_only_fields = [
            "message_id",
            "room",
            "sender",
            "content",
            "timestamp",
            "edited_at",
            "is_deleted",
        ]


class ChatFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ("file",)


class ChatMessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ["content"]
        read_only_fields = ["message_id", "room", "sender", "sent_at", "is_deleted"]

    def update(self, instance, validated_data):
        # Update the content
        instance.content = validated_data.get("content", instance.content)
        # Set the edited_at timestamp to now
        instance.edited_at = datetime.now()
        instance.save()
        return instance


class ChatMessageDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = []

    def update(self, instance, validated_data):
        # Mark the message as deleted
        instance.content = "This message has been deleted."
        instance.edited_at = datetime.now()
        instance.is_deleted = True
        instance.save()
        return instance
