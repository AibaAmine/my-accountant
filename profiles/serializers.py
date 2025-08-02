from rest_framework import serializers
from .models import AccountantProfile
from django.conf import settings


class AccountantProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountantProfile
        fields = [
            "profile_id",
            "bio",
            "profile_picture_url",
            "specializations",
            "certifications",
            "years_of_experience",
            "working_hours",
            "contact_preferences",
            "is_verified",
            "overall_rating",
            "total_completed_sessions",
            "total_reviews_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "profile_id",
            "is_verified",
            "overall_rating",
            "total_completed_sessions",
            "total_reviews_count",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert CloudinaryField to proper Cloudinary URL
        if instance.profile_picture_url:
            # CloudinaryField stores public_id, we need to build the full URL
            data["profile_picture_url"] = (
                f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{instance.profile_picture_url}"
            )
        else:
            data["profile_picture_url"] = None
        return data
