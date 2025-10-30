from django.urls import path
from .views import (
    MyProfileAPIView,
    ProfileInfosApiView,
)

app_name = "profiles"

urlpatterns = [
    # Unified Profile endpoint for all user types (GET & PATCH/PUT)
    path("me/", MyProfileAPIView.as_view(), name="my-profile"),
    
    # Profile Info by user ID (for viewing other users' profiles)
    path("info/<uuid:user_id>/", ProfileInfosApiView.as_view(), name="profile-info"),
]
