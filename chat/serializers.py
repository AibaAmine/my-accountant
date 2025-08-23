from .models import ChatMessages, ChatRooms
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
from accounts.serializers import CustomUserDetailsSerializer

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    creator = CustomUserDetailsSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()

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
            "message_count",
        ]
        read_only_fields = [
            "room_id",
            "creator",
            "created_at",
            "is_private",
            "is_dm",
            "message_count",
        ]

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRooms
        fields = ["room_name", "description", "is_private"]
        read_only_fields = ["room_id", "created_at", "creator", "is_dm"]

class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRooms
        fields = ["room_name", "description", "is_private"]
        read_only_fields = ["room_id", "created_at", "creator", "is_dm"]



class ChatMessageSerializer(serializers.ModelSerializer):
    sender = CustomUserDetailsSerializer(read_only=True)
    room = ChatRoomSerializer(read_only=True)

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


class ChatMessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ["content"]
        read_only_fields = ["message_id", "room", "sender", "timestamp", "is_deleted"]

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
