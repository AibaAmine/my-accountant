from rest_framework import serializers
from .models import AccountantProfile


class AccountantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountantProfile
        fields = [
            "profile_id",
            "user_id",
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
            "user_id",
            "is_verified",
            "overall_rating",
            "total_completed_sessions",
            "total_reviews_count",
            "created_at",
            "updated_at",
        ]


