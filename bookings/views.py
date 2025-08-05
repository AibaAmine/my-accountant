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
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Booking


# todo add filtering and pagination, check if the service, accountant exists before booking

class CreateBookingAPIView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type.lower() != "client":
            raise PermissionDenied("Only clients can create bookings.")

        serializer.save(client_id=user)


class UpdateBookingAPIView(generics.UpdateAPIView):
    serializer_class = BookingUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()

    def get_queryset(self):
        return Booking.objects.filter(client_id=self.request.user)
    
    def perform_update(self, serializer):
        user = self.request.user    
        if user.user_type.lower() != "client":
            raise PermissionDenied("Only clients can update their bookings.")
        serializer.save(client_id=user)

class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type.lower() == "accountant":
            return Booking.objects.filter(accountant_id=user)
        elif user.user_type.lower() == "client":
            return Booking.objects.filter(client_id=user)
        else:
            return Booking.objects.all()


class BookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.user_type.lower() == "accountant":
            booking_id = self.kwargs.get("pk")
            return get_object_or_404(Booking, booking_id=booking_id, accountant_id=user)
        elif user.user_type.lower() == "client":
            booking_id = self.kwargs.get("pk")
            return get_object_or_404(Booking, booking_id=booking_id, client_id=user)
        else:
            return get_object_or_404(Booking, booking_id=booking_id)
