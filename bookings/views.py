from rest_framework import views
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save()


class UpdateBookingAPIView(generics.UpdateAPIView):
    serializer_class = BookingUpdateSerializer
    permission_classes = [IsAuthenticated]
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
            .order_by("-scheduled_start", "-created_at")
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
        user =self.request.user

        # Only allow retrieval when the user is a participant
        return Booking.objects.filter(
            Q(client=user) | Q(accountant=user)
        ).select_related("service", "client", "accountant")
