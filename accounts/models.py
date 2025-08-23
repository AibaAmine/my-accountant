from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from cloudinary.models import CloudinaryField

from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(
        max_length=50,
        choices=[
            ("client", "Client"),
            ("accountant", "Accountant"),
            ("academic", "Academic"),
            ("admin", "Admin"),
        ],
        default="client",
    )
    company_name = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_picture_url = CloudinaryField("image", null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    account_status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
        ],
        default="inactive",
    )
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        from django.core.mail import send_mail

        send_mail(subject, message, from_email, [self.email], **kwargs)


class EmailVerificationOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codes")
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Password reset OTP for {self.user.email} - {self.code}"


class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    admin_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=150, unique=True)
    permissions = models.JSONField(default=list)
    is_private_boolean = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_user"
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"

    def __str__(self):
        return f"Admin: {self.username}"
