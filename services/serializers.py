from rest_framework import serializers
from .models import Service, ServiceCategory
from accounts.serializers import CustomUserDetailsSerializer
from django.utils import timezone


# add more data validation
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
    new_category_name = serializers.CharField(write_only=True, required=False)
    new_category_description = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "category",  # for existing category selection
            "new_category_name",  # for new category creation
            "new_category_description",
            "price",
            "price_negotiable",
            "estimated_duration",
            "duration_unit",
            "deadline",
            "experience_level_required",
            "skills_keywords",
            "urgency_level",
            "location_preference",
            "requirements_notes",
            "attachments",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user", "service_type", "updated_at")

        extra_kwargs = {"category": {"required": False}}

    def validate(self, data):
        user = self.context["request"].user

        if not data.get("category") and not data.get("new_category_name"):
            raise serializers.ValidationError(
                "Either select an existing category or add new one"
            )

        if data.get("category") and data.get("new_category_name"):
            raise serializers.ValidationError(
                "Either select category or create new one not both"
            )

        if not data.get("new_category_name") and data.get("new_category_description"):
            raise serializers.ValidationError(
                "If you provide a new category description, you must also provide a new category name."
            )

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
        new_category_name = validated_data.pop("new_category_name", None)
        new_category_description = validated_data.pop("new_category_description", None)

        if new_category_name:
            category, created = ServiceCategory.objects.get_or_create(
                name=new_category_name.strip(),
                defaults={
                    "description": (
                        new_category_description.strip()
                        if new_category_description
                        else f"Category created for service: {validated_data.get('title', '')}"
                    )
                },
            )
            validated_data["category"] = category

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
    new_category_name = serializers.CharField(
        required=False, write_only=True
    )  # allow users to add new service category when updating their existing service
    new_category_description = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "service_type",
            "title",
            "description",
            "category",
            "new_category_name",
            "new_category_description",
            "price",
            "price_negotiable",
            "estimated_duration",
            "duration_unit",
            "deadline",
            "experience_level_required",
            "skills_keywords",
            "urgency_level",
            "location_preference",
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

        if data.get("category") and data.get("new_category_name"):
            raise serializers.ValidationError(
                "Please either select an existing category OR create a new one, not both."
            )

        if not data.get("new_category_name") and data.get("new_category_description"):
            raise serializers.ValidationError(
                "If you provide a new category description, you must also provide a new category name."
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
        new_category_name = validated_data.pop("new_category_name", None)
        new_category_description = validated_data.pop("new_category_description", None)

        if new_category_name:
            category, created = ServiceCategory.objects.get_or_create(
                name=new_category_name.strip(),
                defaults={
                    "description": (
                        new_category_description.strip()
                        if new_category_description
                        else f"Category created for service: {instance.title}"
                    )
                },
            )
            validated_data["category"] = category

        return super().update(instance, validated_data)
