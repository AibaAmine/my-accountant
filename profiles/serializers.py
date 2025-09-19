from rest_framework import serializers
from .models import AccountantProfile, ClientProfile, AcademicProfile, ProfileAttachment
from accounts.serializers import CustomUserDetailsSerializer


class ProfileAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for profile attachments"""

    url = serializers.SerializerMethodField()
    filename = serializers.CharField(source="original_filename", read_only=True)
    size = serializers.IntegerField(source="file_size", read_only=True)

    class Meta:
        model = ProfileAttachment
        fields = ["attachment_id", "url", "filename", "size", "uploaded_at"]
        read_only_fields = ["attachment_id", "uploaded_at"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class AccountantProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    all_services = serializers.SerializerMethodField()
    all_attachments = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text="Upload multiple files for the profile",
    )

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
            "all_attachments",
            "attachments_count",
            "upload_files",
            "all_services",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "all_attachments",
            "attachments_count",
            "created_at",
            "updated_at",
        ]

    def get_all_services(self, obj):
        """Get all services for this user"""
        from services.serializers import ServiceListSerializer

        services = obj.user.services.filter(is_active=True)
        return ServiceListSerializer(services, many=True, context=self.context).data

    def get_all_attachments(self, obj):
        """Get all profile attachments using serializer with context"""
        attachments = obj.profile_attachments.all()
        return ProfileAttachmentSerializer(
            attachments, many=True, context=self.context
        ).data

    def get_attachments_count(self, obj):
        return obj.profile_attachments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        return data


class ClientProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    all_services = serializers.SerializerMethodField()
    all_attachments = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text="Upload multiple files for the profile",
    )

    class Meta:
        model = ClientProfile
        fields = [
            "profile_id",
            "user",
            "profile_picture",
            "phone",
            "location",
            "activity_type",
            "all_attachments",
            "attachments_count",
            "upload_files",
            "all_services",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "all_attachments",
            "attachments_count",
            "created_at",
            "updated_at",
        ]

    def get_all_services(self, obj):
        """Get all services for this user"""
        from services.serializers import ServiceListSerializer

        services = obj.user.services.filter(is_active=True)
        return ServiceListSerializer(services, many=True, context=self.context).data

    def get_all_attachments(self, obj):
        """Get all profile attachments using serializer with context"""
        attachments = obj.profile_attachments.all()
        return ProfileAttachmentSerializer(
            attachments, many=True, context=self.context
        ).data

    def get_attachments_count(self, obj):
        return obj.profile_attachments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        return data


class AcademicProfileSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    all_attachments = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text="Upload multiple files for the profile",
    )

    class Meta:
        model = AcademicProfile
        fields = [
            "profile_id",
            "user",
            "profile_picture",
            "phone",
            "bio",
            "all_attachments",
            "attachments_count",
            "upload_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "user",
            "all_attachments",
            "attachments_count",
            "created_at",
            "updated_at",
        ]

    def get_all_attachments(self, obj):
        """Get all profile attachments using serializer with context"""
        attachments = obj.profile_attachments.all()
        return ProfileAttachmentSerializer(
            attachments, many=True, context=self.context
        ).data

    def get_attachments_count(self, obj):
        return obj.profile_attachments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle file fields properly
        request = self.context.get("request")
        if instance.profile_picture and request:
            data["profile_picture"] = request.build_absolute_uri(
                instance.profile_picture.url
            )
        return data
