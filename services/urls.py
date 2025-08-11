from .views import (
    ServiceCreateAPIView,
    ServiceDetailAPIView,
    ServiceUpdateAPIView,
    UserServiceListAPIView,
    ServiceDeleteAPIView,
    PublicServiceDetailAPIView,
    PublicServiceListAPIView
)
from django.urls import path

urlpatterns = [
    path("my/", UserServiceListAPIView.as_view(), name="service-list"),
    path("my/<uuid:pk>/", ServiceDetailAPIView.as_view(), name="service-detail"),
    path("create/", ServiceCreateAPIView.as_view(), name="service-create"),
    path(
        "<uuid:pk>/update/",
        ServiceUpdateAPIView.as_view(),
        name="service-update",
    ),
    path(
        "<uuid:pk>/delete/",
        ServiceDeleteAPIView.as_view(),
        name="service-delete",
    ),
    path("browse/",PublicServiceListAPIView.as_view(),name="service_browse"),
    path("browse/<uuid:pk>/",PublicServiceDetailAPIView.as_view(),name="service_view")
]
