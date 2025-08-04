import uuid
from django.db import models
from accounts.models import User
from cloudinary.models import CloudinaryField


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_categories"
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    DURATION_CHOICES = [
        ("hours", "Hours"),
        ("days", "Days"),
        ("weeks", "Weeks"),
        ("months", "Months"),
    ]

    LOCATION_CHOICES = [
        ("online", "Online"),
        ("client_office", "Client's Office"),
        ("my_office", "My Office"),
        ("flexible", "Flexible"),
    ]

    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    service_title = models.CharField(max_length=255)
    service_description = models.TextField()
    service_category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="services"
    )
    estimated_duration = models.PositiveIntegerField(default=1)
    duration_unit = models.CharField(
        max_length=20, choices=DURATION_CHOICES, default="days"
    )
    service_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    can_be_discussed = models.BooleanField(default=False)
    attachments = CloudinaryField("file", null=True, blank=True)
    service_location = models.CharField(
        max_length=50, choices=LOCATION_CHOICES, default="online"
    )
    availability_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service"
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.service_title
