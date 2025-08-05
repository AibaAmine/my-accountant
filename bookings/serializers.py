from rest_framework import serializers
from .models import Booking
from django.utils import timezone


class BookingDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    accountant_name = serializers.SerializerMethodField()
    service_title = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "client_id",
            "client_name",
            "accountant_id",
            "accountant_name",
            "service_id",
            "service_title",
            "scheduled_start",
            "scheduled_end",
            "meeting_type",
            "status",
            "agreed_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["__all__"]

    def get_accountant_name(self, obj):
        return obj.accountant_id.full_name

    def get_client_name(self, obj):
        return obj.client_id.full_name

    def get_service_title(self, obj):
        return obj.service_id.service_title


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "accountant_id",
            "service_id",
            "scheduled_start",
            "scheduled_end",
            "meeting_type",
            "agreed_price",
        ]
        read_only_fields = ["booking_id", "created_at", "updated_at"]

    def validate(self, data):
        if data["scheduled_end"] <= data["scheduled_start"]:
            raise serializers.ValidationError("End time must be after start time")

        if data["scheduled_start"] <= timezone.now():
            raise serializers.ValidationError("Booking must be in the future")
    

        return data

    def validate_accountant_id(self, value):
        if value.user_type != "accountant":
            raise serializers.ValidationError("Selected user is not an accountant")
        return value

class BookingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ["scheduled_start", "scheduled_end", "meeting_type", "status"]
        read_only_fields = ["booking_id", "client_id", "accountant_id", "service_id"]

    def validate(self, data):
        if data["scheduled_end"] <= data["scheduled_start"]:
            raise serializers.ValidationError("End time must be after start time")

        if data["scheduled_start"] <= timezone.now():
            raise serializers.ValidationError("Booking must be in the future")

        return data


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["booking_id", "scheduled_start", "status", "meeting_type"]
        read_only_fields = ["__all__"]
