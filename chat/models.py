import uuid
from django.db import models
from accounts.models import User


# add description field
class ChatRooms(models.Model):

    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_dm = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_chat_rooms",
        null=True,  # Allow rooms to exist without a creator
        blank=True,
    )

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
    room_id = models.ForeignKey(
        ChatRooms, on_delete=models.CASCADE, related_name="members"
    )
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_room_members"
        verbose_name = "Chat Room Member"
        verbose_name_plural = "Chat Room Members"
        unique_together = ("room_id", "user_id")

    def __str__(self):
        return f"{self.user_id.username} in {self.room_id.room_name}"


class UserRoomLastSeen(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_last_seen"
    )
    room = models.ForeignKey(
        ChatRooms, on_delete=models.CASCADE, related_name="user_last_seen"
    )
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_room_last_seen"
        unique_together = ("user", "room")
        verbose_name = "User Room Last Seen"
        verbose_name_plural = "User Room Last Seen"

    def __str__(self):
        return f"{self.user.full_name} last seen {self.room.room_name} at {self.last_seen_at}"

class ChatMessages(models.Model):

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        ChatRooms, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
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

    file = models.FileField(upload_to="chat_files/", blank=True, null=True)

    sent_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_message"
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"Message from {self.sender.id} in {self.room_id.room_name}"


