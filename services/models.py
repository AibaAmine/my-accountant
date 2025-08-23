import uuid
from django.db import models
from accounts.models import User


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
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

#add location field
class Service(models.Model):

    SERVICE_TYPE_CHOICES = [
        ("needed", "Service Needed"),  # Client posting what they need
        ("offered", "Service Offered"),  # Accountant posting what they provide
    ]

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
        ("to_be_discussed", "To Be Discussed"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
        ("any", "Any Level"),
    ]

    URGENCY_CHOICES = [
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("urgent", "Urgent"),
    ]
    

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)

    # Core content
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="services"
    )

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_negotiable = models.BooleanField(default=False)

    # Timeline
    estimated_duration = models.PositiveIntegerField(default=1)
    duration_unit = models.CharField(
        max_length=20, choices=DURATION_CHOICES, default="days"
    )
    deadline = models.DateField(null=True, blank=True)

    # Requirements/Skills (for both offers and services)
    experience_level_required = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default="any"
    )
    skills_keywords = models.TextField(blank=True, help_text="Comma-separated skills")

    # Project specifics
    urgency_level = models.CharField(
        max_length=20, choices=URGENCY_CHOICES, default="medium"
    )
    location_preference = models.CharField(
        max_length=50, choices=LOCATION_CHOICES, default="online"
    )

    # Additional details
    requirements_notes = models.TextField(blank=True)
    attachments = models.FileField(
        upload_to="service_attachments/", null=True, blank=True
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service_type", "is_active"]),
            models.Index(fields=["user", "service_type"]),
            models.Index(fields=["category", "service_type"]),
        ]

    def __str__(self):
        return (
            f"{self.get_service_type_display()}: {self.title} by {self.user.full_name}"
        )
