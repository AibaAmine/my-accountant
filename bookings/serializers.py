from rest_framework import serializers
from .models import Booking
from django.utils import timezone
from services.serializers import ServiceDetailSerializer
from accounts.serializers import CustomUserDetailsSerializer
from django.db.models import Q


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

        req_role = (getattr(request.user, "user_type", "") or "").lower()

        if service.service_type == "offered":
            # Must be: service owner = accountant, requester = client

            if req_role != "client":
                raise serializers.ValidationError(
                    "Only a client can book an offered service."
                )
            if request.user == service.user:
                raise serializers.ValidationError(
                    "You cannot book your own offered service."
                )
            if not data.get("scheduled_start") or not data.get("scheduled_end"):
                raise serializers.ValidationError(
                    "scheduled_start and scheduled_end are required for offered services."
                )

            if data.get("agreed_price") is None:  # new
                raise serializers.ValidationError(
                    {"agreed_price": "Price required for offered service booking."}
                )  # new

        elif service.service_type == "needed":
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

        start = validated_data.get("scheduled_start")
        end = validated_data.get("scheduled_end")

        if start and end:
            if Booking.objects.filter(
                accountant=accountant,
                status__in=["pending", "proposed", "confirmed", "in_progress"],
                scheduled_start__lt=end,
                scheduled_end__gt=start,
            ).exists():
                raise serializers.ValidationError("Time slot already taken.")

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
        fields = [
            "scheduled_start",
            "scheduled_end",
            "meeting_type",
            "status",
            "agreed_price",
            "proposal_message",
        ]
        read_only_fields = ["booking_id", "client", "accountant", "service"]

    def validate(self, data):
        request = self.context.get("request")

        instance = self.instance
        new_status = data.get("status", instance.status)

        provider = instance.accountant
        consumer = instance.client
        service_owner = instance.service.user
        is_provider = request.user == provider
        is_consumer = request.user == consumer
        is_owner = request.user == service_owner

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
        if instance.status in ["confirmed", "in_progress", "completed"] and (
            "scheduled_start" in data or "scheduled_end" in data
        ):
            raise serializers.ValidationError(
                "Schedule cannot be changed after confirmation."
            )

        if "agreed_price" in data:
            if instance.status not in ["pending", "proposed"]:
                raise serializers.ValidationError(
                    "Price can only be set/changed while pending or proposed."
                )
            if data.get("agreed_price") is not None and data.get("agreed_price") < 0:
                raise serializers.ValidationError("Price must be positive.")

        allowed_next = {
            "proposed": {"confirmed", "declined", "cancelled"},
            "pending": {"confirmed", "cancelled"},
            "confirmed": {"in_progress", "cancelled"},
            "in_progress": {"completed", "cancelled"},
            "completed": set(),
            "declined": set(),
            "cancelled": set(),
        }
        if new_status != instance.status:
            if new_status not in allowed_next.get(instance.status, set()):
                raise serializers.ValidationError(
                    f"Cannot transition from {instance.status} to {new_status}."
                )
            if new_status in ["confirmed", "declined"]:
                if not is_owner:
                    raise serializers.ValidationError(
                        "Only the service owner can confirm or decline."
                    )
        if new_status == "in_progress":
            if not is_provider:
                raise serializers.ValidationError(
                    "Only the provider (accountant) can mark in progress."
                )
        if new_status == "completed":
            if not is_consumer:
                raise serializers.ValidationError("Only the client can mark completed.")
        if new_status == "cancelled":
            # Both parties should be able to cancel
            if not (is_provider or is_consumer):
                raise serializers.ValidationError(
                    "Only participants can cancel the booking."
                )

    

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