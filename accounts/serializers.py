from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer

User = get_user_model()


class CustomLoginSerializer(LoginSerializer):

    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={"input_type": "password"})


class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Remove username field completely

    user_type = serializers.ChoiceField(
        choices=[
            ("client", "Client"),
            ("accountant", "Accountant"),
            ("student", "Student"),
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
        user = super().save(request)
        user.full_name = self.validated_data.get("full_name", "")
        user.user_type = self.validated_data.get("user_type")
        user.phone = self.validated_data.get("phone")
        user.save()
        return user


# used for updating users info api
class CustomUserDetailsSerializer(UserDetailsSerializer):

    user_type = serializers.CharField(read_only=True)
    full_name = serializers.CharField()
    company_name = serializers.CharField()
    job_title = serializers.CharField()
    phone = serializers.CharField()
    bio = serializers.CharField()
    profile_picture_url = serializers.URLField(read_only=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    account_status = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "email",
            "full_name",
            "user_type",
            "company_name",
            "job_title",
            "phone",
            "bio",
            "profile_picture_url",
            "is_email_verified",
            "account_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("email", "pk", "created_at", "updated_at")
