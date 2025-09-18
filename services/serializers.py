from rest_framework import serializers
from .models import Service, ServiceCategory, ServiceAttachment
from accounts.serializers import CustomUserDetailsSerializer
from django.utils import timezone
from .category_serializers import ServiceCategorySerializer


class ServiceAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for individual service attachments"""

    class Meta:
        model = ServiceAttachment
        fields = ["id", "file", "original_filename", "file_size", "uploaded_at"]
        read_only_fields = ["id", "original_filename", "file_size", "uploaded_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.file:
            representation["url"] = instance.file.url
            representation["filename"] = instance.original_filename
        return representation


class ServiceListSerializer(serializers.ModelSerializer):
    categories = ServiceCategorySerializer(many=True, read_only=True)
    user = CustomUserDetailsSerializer(read_only=True)
    attachments_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "categories",
            "price",
            "location",
            "location_description",
            "delivery_method",
            "is_featured",
            "attachments_count",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user", "updated_at", "service_type")

    def get_attachments_count(self, obj):
        """Return total number of attachments"""
        return obj.service_attachments.count()


class ServiceDetailSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    all_attachments = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "service_type")

    def get_all_attachments(self, obj):
        """Return all attachments including legacy and new ones"""
        return obj.get_all_attachments()


class AccountantServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for accountants viewing service details (their offered services or client requests)"""

    user = CustomUserDetailsSerializer(read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    all_attachments = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "categories",
            "price",
            "price_description",
            "estimated_duration",
            "duration_unit",
            "estimated_duration_description",
            "location",
            "delivery_method",
            "all_attachments",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "user", "created_at", "updated_at", "service_type")

    def get_all_attachments(self, obj):
        """Return all attachments including legacy and new ones"""
        return obj.get_all_attachments()


class ClientServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for clients viewing service details (their requests or accountant offers)"""

    user = CustomUserDetailsSerializer(read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    all_attachments = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "categories",
            "tasks_and_responsibilities",
            "conditions_requirements",
            "estimated_duration",
            "duration_unit",
            "estimated_duration_description",
            "price",
            "price_description",
            "location",
            "delivery_method",
            "all_attachments",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "user", "created_at", "updated_at", "service_type")

    def get_all_attachments(self, obj):
        """Return all attachments including legacy and new ones"""
        return obj.get_all_attachments()


class ServiceCreateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=True
    )
    # Accept multiple files for upload
    upload_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "categories",  # list of existing category IDs
            "price",
            "price_description",
            "estimated_duration",
            "duration_unit",
            "estimated_duration_description",
            "tasks_and_responsibilities",
            "conditions_requirements",
            "location",
            "location_description",
            "delivery_method",
            "upload_files", 
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user", "service_type", "updated_at")

    def validate_categories(self, value):
        """Validate that all provided category IDs exist and are active"""
        if not value:
            raise serializers.ValidationError("At least one category must be selected.")

        existing_categories = ServiceCategory.objects.filter(
            id__in=value, is_active=True
        )
        if len(existing_categories) != len(value):
            raise serializers.ValidationError(
                "One or more selected categories are invalid or inactive."
            )
        return value

    def validate(self, data):
        user = self.context["request"].user

        # Set service_type based on user type
        if user.user_type.lower() == "client":
            data["service_type"] = "needed"
        elif user.user_type.lower() == "accountant":
            data["service_type"] = "offered"
        else:
            raise serializers.ValidationError("Invalid user type.")

        if "price" in data and data["price"] and data["price"] < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        if (
            "estimated_duration" in data
            and data["estimated_duration"]
            and data["estimated_duration"] <= 0
        ):
            raise serializers.ValidationError("Duration must be greater than zero.")
        return data

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        upload_files = validated_data.pop("upload_files", [])

        # Create the service first
        service = super().create(validated_data)

        # Add the categories
        if categories:
            existing_categories = ServiceCategory.objects.filter(id__in=categories)
            service.categories.add(*existing_categories)

        # Handle multiple file uploads
        if upload_files:
            for file in upload_files:
                ServiceAttachment.objects.create(
                    service=service, file=file, original_filename=file.name
                )

        return service

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Include the full categories objects in response
        if instance.categories.exists():
            representation["categories"] = ServiceCategorySerializer(
                instance.categories.all(), many=True
            ).data
        else:
            representation["categories"] = []

        # Include all attachments (new system)
        representation["all_attachments"] = instance.get_all_attachments()

        return representation


class ServiceUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    # Accept multiple files for upload
    upload_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    # Option to remove specific attachments
    remove_attachment_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "categories",
            "price",
            "price_description",
            "estimated_duration",
            "duration_unit",
            "estimated_duration_description",
            "tasks_and_responsibilities",
            "conditions_requirements",
            "location",
            "location_description",
            "delivery_method",
            "upload_files",  
            "remove_attachment_ids",  
        ]
        read_only_fields = ("id", "user", "service_type", "created_at", "updated_at")

    def validate_categories(self, value):
        """Validate that all provided category IDs exist and are active"""
        if value:  # Only validate if categories are provided
            existing_categories = ServiceCategory.objects.filter(
                id__in=value, is_active=True
            )
            if len(existing_categories) != len(value):
                raise serializers.ValidationError(
                    "One or more selected categories are invalid or inactive."
                )
        return value

    def validate(self, data):
        user = self.context["request"].user
        service = self.instance

        if user != service.user:
            raise serializers.ValidationError(
                "You do not have permission to update this service."
            )

        if service.is_active is False:
            raise serializers.ValidationError(
                "This service is not active and cannot be updated."
            )

        if "price" in data and data["price"] and data["price"] < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        if (
            "estimated_duration" in data
            and data["estimated_duration"]
            and data["estimated_duration"] <= 0
        ):
            raise serializers.ValidationError("Duration must be greater than zero.")

        return data

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        upload_files = validated_data.pop("upload_files", [])
        remove_attachment_ids = validated_data.pop("remove_attachment_ids", [])

        # Update the service first
        service = super().update(instance, validated_data)

        # Handle categories update if provided
        if categories is not None:
            # Clear existing categories and add new ones
            service.categories.clear()
            if categories:
                existing_categories = ServiceCategory.objects.filter(id__in=categories)
                service.categories.add(*existing_categories)

        # Remove specified attachments
        if remove_attachment_ids:
            ServiceAttachment.objects.filter(
                service=service, id__in=remove_attachment_ids
            ).delete()

        # Add new files
        if upload_files:
            for file in upload_files:
                ServiceAttachment.objects.create(
                    service=service, file=file, original_filename=file.name
                )

        return service

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Include the full categories objects in response
        if instance.categories.exists():
            representation["categories"] = ServiceCategorySerializer(
                instance.categories.all(), many=True
            ).data
        else:
            representation["categories"] = []

        # Include all attachments (new system)
        representation["all_attachments"] = instance.get_all_attachments()

        return representation
