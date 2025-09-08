from rest_framework import serializers
from .models import Service, ServiceCategory
from accounts.serializers import CustomUserDetailsSerializer
from django.utils import timezone


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceListSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    user = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "category",
            "price",
            "price_negotiable",
            "location_preference",
            "location",
            "urgency_level",
            "is_featured",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user", "updated_at", "service_type")


class ServiceDetailSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "service_type")


class ServiceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "category",  # for existing category selection
            "price",
            "price_negotiable",
            "estimated_duration",
            "duration_unit",
            "deadline",
            "experience_level_required",
            "skills_keywords",
            "urgency_level",
            "location_preference",
            "location",
            "requirements_notes",
            "attachments",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user", "service_type", "updated_at")

        extra_kwargs = {"category": {"required": True}}

    def validate(self, data):
        user = self.context["request"].user

        if not data.get("category"):
            raise serializers.ValidationError("Please select an existing category")

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
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.attachments:
            representation["attachments"] = {
                "url": instance.attachments.url,
                "filename": (
                    instance.attachments.name.split("/")[-1]
                    if instance.attachments.name
                    else "file"
                ),
            }
        else:
            representation["attachments"] = None

        # Include the full category object in response
        if instance.category:
            representation["category"] = ServiceCategorySerializer(
                instance.category
            ).data
        return representation


class ServiceUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "category",
            "price",
            "price_negotiable",
            "estimated_duration",
            "duration_unit",
            "deadline",
            "experience_level_required",
            "skills_keywords",
            "urgency_level",
            "location_preference",
            "location",
            "requirements_notes",
            "attachments",
        ]
        read_only_fields = ("id", "user", "service_type", "created_at", "updated_at")

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

        if "deadline" in data and data["deadline"]:

            if data["deadline"] < timezone.now().date():
                raise serializers.ValidationError("Deadline cannot be in the past.")

        if "category" in data and data["category"]:
            if not data["category"].is_active:
                raise serializers.ValidationError("Selected category is not active.")

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Include the full category object in response
        if instance.category:
            representation["category"] = ServiceCategorySerializer(
                instance.category
            ).data
        return representation

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
