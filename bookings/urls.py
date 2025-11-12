from .views import (
    CreateBookingAPIView,
    UpdateBookingAPIView,
    BookingListAPIView,
    BookingReceivedListAPIView,
    BookingDetailAPIView,
    AcceptBookingAPIView,
    DeclineBookingAPIView,
)

from django.urls import path

urlpatterns = [
    path("bookings/", BookingListAPIView.as_view(), name="booking-list"),
    path("bookings/received/", BookingReceivedListAPIView.as_view(), name="booking-received-list"),
    path("bookings/create/", CreateBookingAPIView.as_view(), name="booking-create"),
    path(
        "bookings/<uuid:booking_id>/",
        BookingDetailAPIView.as_view(),
        name="booking-detail",
    ),
    path(
        "bookings/<uuid:booking_id>/update/",
        UpdateBookingAPIView.as_view(),
        name="booking-update",
    ),
    path(
        "bookings/<uuid:booking_id>/accept/",
        AcceptBookingAPIView.as_view(),
        name="booking-accept",
    ),
    path(
        "bookings/<uuid:booking_id>/decline/",
        DeclineBookingAPIView.as_view(),
        name="booking-decline",
    ),
]
