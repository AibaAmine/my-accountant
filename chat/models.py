import uuid
from django.db import models
from accounts.models import User


class ChatRooms(models.Model):

    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=255, unique=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_rooms"
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def __str__(self):
        return self.room_name


class ChatMembers(models.Model):

    room_member_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    room_id = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_room_members"
        verbose_name = "Chat Room Member"
        verbose_name_plural = "Chat Room Members"
        unique_together = ("room_id", "user_id")

    def __str__(self):
        return f"{self.user_id.username} in {self.room_id.room_name}"


class ChatMessages(models.Model):

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_id = models.ForeignKey(
        ChatRooms, on_delete=models.CASCADE, related_name="messages"
    )
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(
        max_length=50,
        choices=[
            ("text", "Text"),
            ("image", "Image"),
            ("file", "File"),
            ("voice", "Voice"),
        ],
        default="text",
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        db_table = "chat_message"
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
       

    def __str__(self):
        return f"Message from {self.sender_id.username} in {self.room_id.room_name}"
