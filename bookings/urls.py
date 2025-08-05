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
    path("bookings/<uuid:pk>/", BookingDetailAPIView.as_view(), name="booking-detail"),
    path("bookings/<uuid:pk>/update/", UpdateBookingAPIView.as_view(), name="booking-update"),
]