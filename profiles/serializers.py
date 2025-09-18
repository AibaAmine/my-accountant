from rest_framework import serializers
from .models import AccountantProfile, ClientProfile, AcademicProfile
from accounts.serializers import CustomUserDetailsSerializer


class AccountantProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    all_services = serializers.SerializerMethodField()

    class Meta:
        model = AccountantProfile
        fields = [
            "profile_id",
            "user",
            "profile_picture",
            "phone",
            "location",
            "bio",
            "working_hours",
            "attachments",
            "all_services",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "created_at",
            "updated_at",
        ]

    def get_all_services(self, obj):
        """Get all services for this user"""
        from services.serializers import ServiceSerializer

        services = obj.user.services.filter(is_active=True)
        return ServiceSerializer(services, many=True, context=self.context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        if instance.attachments and request:
            data["attachments"] = request.build_absolute_uri(instance.attachments.url)
        return data


class ClientProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    all_services = serializers.SerializerMethodField()

    class Meta:
        model = ClientProfile
        fields = [
            "profile_id",
            "user",
            "profile_picture",
            "phone",
            "location",
            "activity_type",
            "attachments",
            "all_services",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "created_at",
            "updated_at",
        ]

    def get_all_services(self, obj):
        """Get all services for this user"""
        from services.serializers import ServiceSerializer

        services = obj.user.services.filter(is_active=True)
        return ServiceSerializer(services, many=True, context=self.context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        if instance.attachments and request:
            data["attachments"] = request.build_absolute_uri(instance.attachments.url)
        return data


class AcademicProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = AcademicProfile
        fields = [
            "profile_id",
            "user",
            "profile_picture",
            "phone",
            "bio",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        if instance.attachments and request:
            data["attachments"] = request.build_absolute_uri(instance.attachments.url)
        return data
