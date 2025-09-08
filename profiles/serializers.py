from rest_framework import serializers
from .models import AccountantProfile, ClientProfile, AcademicProfile


class AccountantProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AccountantProfile
        fields = [
            "profile_id",
            "full_name",
            "profile_picture",
            "phone",
            "location",
            "bio",
            "working_hours",
            "attachments",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "full_name",
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


class ClientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            "profile_id",
            "full_name",
            "profile_picture",
            "phone",
            "location",
            "activity_type",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "full_name",
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


class AcademicProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AcademicProfile
        fields = [
            "profile_id",
            "full_name",
            "profile_picture",
            "phone",
            "bio",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "full_name",
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
