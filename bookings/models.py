import uuid
from django.db import models
from accounts.models import User
from services.models import Service


class Booking(models.Model):

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_bookings"
    )
    accountant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accountant_bookings"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    proposal_message = models.TextField(blank=True, null=True)

    # Booking details
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    meeting_type = models.CharField(
        max_length=50,
        choices=[
            ("online", "Online"),
            ("in_person", "In Person"),
            ("phone", "Phone"),
        ],
        default="online",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("proposed", "Proposed"),  # initial for service_proposal
            ("pending", "Pending"),  # initial for direct booking awaiting confirmation
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("declined", "Declined"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
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
        return f"Booking {self.booking_id}: {self.client.username} with {self.accountant.username}"
