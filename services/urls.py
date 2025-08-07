from .views import (
    ServiceCreateAPIView,
    ServiceDetailAPIView,
    ServiceUpdateAPIView,
    UserServiceListAPIView,
    ServiceDeleteAPIView,
)
from django.urls import path

urlpatterns = [
    path("services/me/", UserServiceListAPIView.as_view(), name="service-list"),
    path("services/<uuid:pk>/", ServiceDetailAPIView.as_view(), name="service-detail"),
    path("services/create/", ServiceCreateAPIView.as_view(), name="service-create"),
    path(
        "services/<uuid:pk>/update/",
        ServiceUpdateAPIView.as_view(),
        name="service-update",
    ),
    path(
        "services/<uuid:pk>/delete/",
        ServiceDeleteAPIView.as_view(),
        name="service-delete",
    ),
]
