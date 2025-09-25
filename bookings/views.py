from rest_framework import views
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    BookingListSerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingUpdateSerializer,
)
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Booking


class CreateBookingAPIView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save()


class UpdateBookingAPIView(generics.UpdateAPIView):
    serializer_class = BookingUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "booking_id"

    def get_queryset(self):
        user = self.request.user
        # Only allow updates on bookings where the user is a participant
        return Booking.objects.filter(
            Q(client=user) | Q(accountant=user)
        ).select_related("service", "client", "accountant")

    def perform_update(self, serializer):

        serializer.save()


class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Booking.objects.all()
            .select_related("service", "client", "accountant")
            .order_by("-created_at")
        )

        user_type = getattr(user, "user_type", "") or ""
        if user_type.lower() == "accountant":
            return qs.filter(accountant=user)
        if user_type.lower() == "client":
            return qs.filter(client=user)
        return qs


class BookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "booking_id"

    def get_queryset(self):
        user = self.request.user

        # Only allow retrieval when the user is a participant
        return Booking.objects.filter(
            Q(client=user) | Q(accountant=user)
        ).select_related("service", "client", "accountant")


class AcceptBookingAPIView(views.APIView):
    """
    Accept a booking - only the service owner can accept
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.select_related(
                "service", "client", "accountant"
            ).get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is the service owner (the one who can accept/decline)
        if request.user != booking.service.user:
            return Response(
                {"error": "Only the service owner can accept this booking"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if booking is in acceptable status
        if booking.status not in ["pending", "proposed"]:
            return Response(
                {"error": f"Cannot accept booking with status: {booking.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Accept the booking
        booking.status = "confirmed"
        booking.save()

        return Response(
            {
                "message": "Booking accepted successfully",
                "booking_id": str(booking.booking_id),
                "status": booking.status,
                "client_id": str(booking.client.id),
                "accountant_id": str(booking.accountant.id),
            },
            status=status.HTTP_200_OK,
        )


class DeclineBookingAPIView(views.APIView):
    """
    Decline a booking - only the service owner can decline
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.select_related("service").get(
                booking_id=booking_id
            )
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is the service owner (the one who can accept/decline)
        if request.user != booking.service.user:
            return Response(
                {"error": "Only the service owner can decline this booking"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status not in ["pending", "proposed"]:
            return Response(
                {"error": f"Cannot decline booking with status: {booking.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = "declined"
        booking.save()

        return Response(
            {
                "message": "Booking declined successfully",
                "booking_id": str(booking.booking_id),
                "status": booking.status,
            },
            status=status.HTTP_200_OK,
        )
