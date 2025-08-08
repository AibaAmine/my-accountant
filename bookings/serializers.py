from rest_framework import serializers
from .models import Booking
from django.utils import timezone
from services.serializers import ServiceDetailSerializer
from accounts.serializers import CustomUserDetailsSerializer


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
            "scheduled_start",
            "scheduled_end",
            "meeting_type",
            "agreed_price",
            "proposal_message",
        ]
        read_only_fields = ["booking_id", "created_at", "updated_at"]

    def validate(self, data):
        request = self.context.get("request")

        service = data.get("service")

        if service is None:
            raise serializers.ValidationError({"service": "This field is required."})

        if service.service_type == "offered":
            # Client booking an accountant's offered service
            if request.user == service.user:
                raise serializers.ValidationError(
                    "You cannot book your own offered service."
                )

            if not data.get("scheduled_start") or not data.get("scheduled_end"):
                raise serializers.ValidationError(
                    "scheduled_start and scheduled_end are required for offered services."
                )

        elif service.service_type == "needed":
            # Accountant proposing to client's needed service
            if request.user == service.user:
                raise serializers.ValidationError(
                    "You cannot propose to your own needed service."
                )
        else:
            raise serializers.ValidationError({"service": "Unsupported service_type."})

        # Time validations if both provided
        start = data.get("scheduled_start")
        end = data.get("scheduled_end")
        if (start and not end) or (end and not start):
            raise serializers.ValidationError(
                "Provide both scheduled_start and scheduled_end, or neither."
            )
        if start and end:
            if end <= start:
                raise serializers.ValidationError("End time must be after start time.")
            if start <= timezone.now():
                raise serializers.ValidationError("Booking must be in the future.")

        if data.get("agreed_price") is None:
            raise serializers.ValidationError(
                {"agreed_price": "This field is required."}
            )

        return data

    def create(self, validated_data):
        service = validated_data["service"]
        request = self.context["request"]

        # Decide parties and initial status from service.service_type
        if service.service_type == "offered":
            client = request.user
            accountant = service.user
            initial_status = "pending"
        else:  # "needed"
            client = service.user
            accountant = request.user

            initial_status = "proposed"

        booking = Booking.objects.create(
                client=client,
                accountant=accountant,
                status=initial_status,
                **validated_data,
            )

        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ["scheduled_start", "scheduled_end", "meeting_type", "status"]
        read_only_fields = ["booking_id", "client", "accountant", "service"]

    def validate(self, data):
        request = self.context.get("request")

        instance = self.instance
        new_status = data.get("status", instance.status)

        start = data.get("scheduled_start", instance.scheduled_start)
        end = data.get("scheduled_end", instance.scheduled_end)
        if (start and not end) or (end and not start):
            raise serializers.ValidationError(
                "Provide both scheduled_start and scheduled_end, or neither."
            )
        if start and end:
            if end <= start:
                raise serializers.ValidationError("End time must be after start time.")
            if start <= timezone.now():
                raise serializers.ValidationError("Booking must be in the future.")

        # Only the service owner confirms/declines (works for both flows)
        is_service_owner = request.user == instance.service.user
        if instance.status in ["pending", "proposed"]:
            if new_status in ["confirmed", "declined"] and not is_service_owner:
                raise serializers.ValidationError(
                    "Only the service owner may confirm or decline this booking."
                )

        if (
            instance.status in ["declined", "completed", "cancelled"]
            and new_status != instance.status
        ):
            raise serializers.ValidationError("This booking is no longer editable.")

        return data


class BookingListSerializer(serializers.ModelSerializer):
    service = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "service",
            "scheduled_start",
            "scheduled_end",
            "status",
            "meeting_type",
            "created_at",
        ]
        read_only_fields = fields
