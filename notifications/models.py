from django.db import models
import uuid
from accounts.models import User

# Create your models here.


class Notification(models.Model):

    notification_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    NOTIFICATION_TYPE = [
        ("booking_created", "New Booking Request"),
        ("booking_accepted", "Booking Confirmed"),
        ("booking_declined", "Booking Declined"),
        ("message", "New Message"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField(max_length=255)

    is_read = models.BooleanField(default=False)

    related_object_id = models.UUIDField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this notification was created"
    )

    class Meta:
        ordering = ["-created_at"] 
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.email}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])



