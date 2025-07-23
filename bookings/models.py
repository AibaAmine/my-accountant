import uuid
from django.db import models
from accounts.models import User
from services.models import Service


class Booking(models.Model):

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_bookings"
    )
    accountant_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accountant_bookings"
    )
    service_id = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="bookings"
    )

    # Booking details
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    meeting_type = models.CharField(
        max_length=50,
        choices=[
            ("online", "Online"),
            ("in_person", "In Person"),
            ("phone", "Phone"),
        ],
        default="online",
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("scheduled", "Scheduled"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
    )
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking"
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["-scheduled_start"]

    def __str__(self):
        return f"Booking {self.booking_id}: {self.client_id.username} with {self.accountant_id.username}"
