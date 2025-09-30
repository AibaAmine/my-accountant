from django.urls import path
from .views import (
    AccountantProfileAPIView,
    ClientProfileAPIView,
    AcademicProfileAPIView,
    ProfileInfosApiView,
)

app_name = "profiles"

urlpatterns = [
    # Accountant Profile URLs
    path("accountant/", AccountantProfileAPIView.as_view(), name="accountant-profile"),
    # Client Profile URLs
    path("client/", ClientProfileAPIView.as_view(), name="client-profile"),
    # Academic Profile URLs
    path("academic/", AcademicProfileAPIView.as_view(), name="academic-profile"),
    # Profile Info by user ID
    path("info/<uuid:user_id>/", ProfileInfosApiView.as_view(), name="profile-info"),
]
