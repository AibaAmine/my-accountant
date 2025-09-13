from rest_framework import serializers
from .models import ServiceCategory


class ServiceCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "created_by")

    def validate_name(self, value):
        """Ensure category name is unique (case-insensitive)"""
        if ServiceCategory.objects.filter(name__iexact=value.strip()).exists():
            raise serializers.ValidationError(
                "A category with this name already exists."
            )
        return value.strip()

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class ServiceCategorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
        )
