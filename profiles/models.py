import uuid
from django.db import models
from accounts.models import User


class AccountantProfile(models.Model):
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user= models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="accountant_profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/accountants/", null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    working_hours = models.JSONField(default=dict)

    attachments = models.FileField(
        upload_to="documents/accountants/attachments/", null=True, blank=True
    )
    
    is_available = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accountant_profiles"
        verbose_name = "Accountant Profile"
        verbose_name_plural = "Accountant Profiles"

    def __str__(self):
        return f"Accountant: {self.user.full_name}"


class ClientProfile(models.Model):
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/clients/", null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    activity_type = models.CharField(max_length=255, blank=True)

    attachments = models.FileField(
        upload_to="documents/clients/attachments/", null=True, blank=True
    )

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "client_profiles"
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def __str__(self):
        return f"Client: {self.user.full_name}"


class AcademicProfile(models.Model):
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="academic_profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/academics/", null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attachments = models.FileField(
        upload_to="documents/academics/attachments/", null=True, blank=True
    )

    class Meta:
        db_table = "academic_profiles"
        verbose_name = "Academic Profile"
        verbose_name_plural = "Academic Profiles"

    def __str__(self):
        return f"Academic: {self.user.full_name}"
