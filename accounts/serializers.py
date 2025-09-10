from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer
import random
from .models import EmailVerificationOTP, PasswordResetOTP
from django.conf import settings

from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class CustomLoginSerializer(LoginSerializer):

    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Check if user exists with this email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"email": "No user found with this email address."}
                )

            # Check if password is correct
            if not user.check_password(password):
                raise serializers.ValidationError({"password": "Incorrect password."})

            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    {"email": "This account is not activated."}
                )

            user.backend = "django.contrib.auth.backends.ModelBackend"

            attrs["user"] = user
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Remove username field completely

    user_type = serializers.ChoiceField(
        choices=[
            ("client", "Client"),
            ("accountant", "Accountant"),
            ("academic", "Academic"),
            ("admin", "Admin"),
        ],
        required=True,
    )

    full_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )

    phone = serializers.CharField(max_length=20, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            del self.fields["username"]
        self._has_phone_field = False

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with that email address already exists."
            )
        return email

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["full_name"] = self.validated_data.get("full_name", "")
        data["user_type"] = self.validated_data.get("user_type")
        data["phone"] = self.validated_data.get("phone", "")
        return data

    def save(self, request):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User(
            email=self.validated_data["email"],
            full_name=self.validated_data.get("full_name", ""),
            user_type=self.validated_data.get("user_type"),
            phone=self.validated_data.get("phone", ""),
            is_active=False,  # Require OTP verification before activation
        )

        user.set_password(self.validated_data["password1"])

        user.save()

        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):

    user_type = serializers.CharField(read_only=True)
    full_name = serializers.CharField()
    phone = serializers.CharField()
    is_email_verified = serializers.BooleanField(read_only=True)
    account_status = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "email",
            "full_name",
            "user_type",
            "phone",
            "is_email_verified",
            "account_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "email",
            "pk",
            "created_at",
            "updated_at",
            "user_type",
            "is_email_verified",
            "account_status",
        )


# for Generates & sends OTP
class SendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.is_active:
            raise serializers.ValidationError("This email is allready validated ")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        print("[DEBUG] About to create EmailVerificationOTP in serializer")
        code = str(random.randint(100000, 999999))
        EmailVerificationOTP.objects.create(
            user=user, code=code, expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f" OTP for {email} : {code}")
        return user


# for Checks OTP & activates account
class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp_code = attrs.get("otp_code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        try:
            otp = EmailVerificationOTP.objects.get(
                user=user, code=otp_code, is_used=False
            )
        except EmailVerificationOTP.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "Invalid OTP."})

        if otp.is_expired():
            raise serializers.ValidationError({"otp_code": "OTP expired."})

        attrs["user"] = user
        attrs["otp"] = otp

        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        user.is_active = True
        user.account_status = "active"
        user.is_email_verified = True
        user.save()

        otp.is_used = True
        otp.save()

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with that email.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        PasswordResetOTP.objects.create(user=user, code=code, expires_at=expires_at)

        # existing method to send email
        user.email_user(
            subject="Your Password Reset Code",
            message=f"Your OTP code for password reset is {code}. It expires in 10 minutes.",
        )

        return user


class VerifyPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("otp_code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        try:
            otp = PasswordResetOTP.objects.get(user=user, code=code, is_used=False)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "Invalid OTP."})

        if otp.is_expired():
            raise serializers.ValidationError({"otp_code": "OTP expired."})

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]
        new_password = self.validated_data["new_password"]

        # method to set the new password as hash
        user.set_password(new_password)
        user.save()

        otp.is_used = True
        otp.save()
