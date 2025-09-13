from .serializers import (
    ServiceListSerializer,
    ServiceDetailSerializer,
    AccountantServiceDetailSerializer,
    ClientServiceDetailSerializer,
    ServiceCreateSerializer,
    ServiceUpdateSerializer,
)
from .category_serializers import (
    ServiceCategorySerializer,
    ServiceCategoryCreateSerializer,
)

from rest_framework import generics
from .models import Service, ServiceCategory
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ServiceFilter


class ServiceCreateAPIView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class ServiceUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ServiceUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Service.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        return Service.objects.filter(user=self.request.user, is_active=True)

    def perform_update(self, serializer):
        user = self.request.user

        serializer.save(user=user)


class PublicServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = [
        "title",
        "description",
        "user__full_name",
        "categories__name",
    ]
    ordering_fields = ["created_at", "price", "estimated_duration"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        role = (getattr(user, "user_type", "") or "").lower()
        if role == "client":
            return Service.objects.filter(
                is_active=True, service_type="offered"
            ).exclude(user=user)

        if role == "accountant":
            return Service.objects.filter(
                is_active=True, service_type="needed"
            ).exclude(user=user)
        return Service.objects.none()


class PublicServiceDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_serializer_class(self):
        
        service = self.get_object()

        if service.service_type == "offered":
           
            return AccountantServiceDetailSerializer
        elif service.service_type == "needed":
            
            return ClientServiceDetailSerializer
        return ServiceDetailSerializer

    def get_queryset(self):
        user = self.request.user
        role = (getattr(user, "user_type", "") or "").lower()

        if role == "client":
            return (
                Service.objects.filter(is_active=True, service_type="offered")
                .select_related("user")
                .prefetch_related("categories")
                .exclude(user=user)
            )
        if role == "accountant":
            return (
                Service.objects.filter(is_active=True, service_type="needed")
                .select_related("user")
                .prefetch_related("categories")
                .exclude(user=user)
            )
        return None


class UserServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Service.objects.filter(user=self.request.user, is_active=True)
            .select_related("user")
            .prefetch_related("categories")
            .order_by("-created_at")
        )


class ServiceDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_serializer_class(self):
        """Return serializer based on the SERVICE TYPE being viewed, not user role"""
        # Get the service instance to check its type
        service = self.get_object()

        if service.service_type == "offered":
            # Viewing an accountant's offered service - show service details (price, duration, etc.)
            return AccountantServiceDetailSerializer
        elif service.service_type == "needed":
            # Viewing a client's needed service - show request details (tasks, conditions, etc.)
            return ClientServiceDetailSerializer
        return ServiceDetailSerializer

    def get_queryset(self):
        return (
            Service.objects.filter(user=self.request.user, is_active=True)
            .select_related("user")
            .prefetch_related("categories")
        )


class ServiceDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        # Only allow deleting own active services
        return Service.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        # Soft delete: mark as inactive
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"detail": "Service deleted successfully."}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Service not found or already deleted."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ServiceCategoryListAPIView(generics.ListAPIView):
    """
    List only default (admin-created) service categories for dropdown
    """

    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True).order_by("name")


class ServiceCategoryDetailAPIView(generics.RetrieveAPIView):
    """
    Get a specific category by ID.

    """

    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True)
