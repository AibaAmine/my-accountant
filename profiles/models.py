import uuid
from django.db import models
from accounts.models import User


class AccountantProfile(models.Model):

    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="accountant_profile"
    )
    bio = models.TextField(blank=True)
    profile_picture_url = models.URLField(blank=True, null=True)
    specializations = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    years_of_experience = models.IntegerField(default=0)
    working_hours = models.JSONField(default=dict)
    contact_preferences = models.JSONField(default=dict)
    is_verified = models.BooleanField(default=False)
    overall_rating = models.FloatField(default=0.0)
    total_completed_sessions = models.IntegerField(default=0)
    total_reviews_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Accountant_profile"
        verbose_name = "Accountant Profile"
        verbose_name_plural = "Accountant Profiles"

    def __str__(self):
        return f"Accountant: {self.user_id.username}"
