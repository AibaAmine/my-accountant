from .views import (
    CreateBookingAPIView,
    UpdateBookingAPIView,
    BookingListAPIView,
    BookingDetailAPIView,
)
    
from django.urls import path

urlpatterns = [
    path("bookings/", BookingListAPIView.as_view(), name="booking-list"),
    path("bookings/create/", CreateBookingAPIView.as_view(), name="booking-create"),
    path("bookings/<uuid:booking_id>/", BookingDetailAPIView.as_view(), name="booking-detail"),
    path("bookings/<uuid:booking_id>/update/", UpdateBookingAPIView.as_view(), name="booking-update"),
]