from rest_framework import serializers
from .models import Booking
from django.utils import timezone
from services.serializers import ServiceDetailSerializer
from accounts.serializers import CustomUserDetailsSerializer
from django.db.models import Q
from services.serializers import ServiceDetailSerializer


class BookingDetailSerializer(serializers.ModelSerializer):
    client = CustomUserDetailsSerializer(read_only=True)
    accountant = CustomUserDetailsSerializer(read_only=True)
    service = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "booking_id",
            "created_at",
            "updated_at",
            "client",
            "accountant",
            "service",
        ]


class BookingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "service",
            "full_name",
            "linkedin_url",
            "cv_file",
            "additional_notes",
        ]
        read_only_fields = ["booking_id", "created_at", "updated_at"]

    def validate(self, data):
        request = self.context.get("request")
        service = data.get("service")

        if service is None:
            raise serializers.ValidationError({"service": "This field is required."})

        req_role = (getattr(request.user, "user_type", "") or "").lower()

        if service.service_type == "offered":
            # Client booking accountant's offered service
            if req_role != "client":
                raise serializers.ValidationError(
                    "Only a client can book an offered service."
                )
        elif service.service_type == "needed":
            # Accountant proposing to client's needed service
            if req_role != "accountant":
                raise serializers.ValidationError(
                    "Only an accountant can propose to a needed service."
                )
            if request.user == service.user:
                raise serializers.ValidationError(
                    "You cannot propose to your own needed service."
                )
        else:
            raise serializers.ValidationError({"service": "Unsupported service_type."})

        return data

    def create(self, validated_data):
        service = validated_data["service"]
        request = self.context["request"]

        # Decide parties from service.service_type
        if service.service_type == "offered":
            client = request.user
            accountant = service.user
        else:  # "needed"
            client = service.user
            accountant = request.user

        booking = Booking.objects.create(
            client=client,
            accountant=accountant,
            status="pending",
            **validated_data,
        )

        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "status",
            "full_name",
            "linkedin_url",
            "cv_file",
            "additional_notes",
        ]
        read_only_fields = ["booking_id", "client", "accountant", "service"]

    def validate(self, data):
        request = self.context.get("request")
        instance = self.instance
        new_status = data.get("status", instance.status)

        provider = instance.accountant
        consumer = instance.client
        service_owner = instance.service.user
        is_owner = request.user == service_owner

        # Status transition validation
        allowed_transitions = {
            "pending": ["confirmed", "declined"],
            "confirmed": [],  # No further transitions needed
            "declined": [],  # Final state
        }

        if new_status != instance.status:
            if new_status not in allowed_transitions.get(instance.status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {instance.status} to {new_status}."
                )
            if new_status in ["confirmed", "declined"]:
                if not is_owner:
                    raise serializers.ValidationError(
                        "Only the service owner can confirm or decline."
                    )

        return data


class BookingListSerializer(serializers.ModelSerializer):
    service = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "service",
            "status",
            "created_at",
        ]
