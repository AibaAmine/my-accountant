import uuid
from django.db import models
from accounts.models import User
from services.models import Service


class Booking(models.Model):

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="service_requester_bookings"
    )
    accountant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accountant_bookings"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    full_name = models.CharField(max_length=255)
    linkedin_url = models.URLField(blank=True, null=True)
    cv_file = models.FileField(upload_to="booking_cvs/", blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),  
            ("confirmed", "Confirmed"),  
            ("declined", "Declined"),  
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking"
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking {self.booking_id}: {self.client.full_name} with {self.accountant.full_name}"
