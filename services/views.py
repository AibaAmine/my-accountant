from .serializers import (   
    ServiceListSerializer,
    ServiceDetailSerializer,
    ServiceCreateSerializer,
    ServiceUpdateSerializer,

    )

from rest_framework import generics 
from .models import Service, ServiceCategory
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class ServiceCreateAPIView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class ServiceUpdateAPIView(generics.UpdateAPIView):
    serializer_class=ServiceUpdateSerializer     
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset= Service.objects.all()
    lookup_field="pk"
    
    def get_queryset(self):
        return Service.objects.filter(user=self.request.user,is_active=True)
    
    def perform_update(self,serializer):
        user = self.request.user
        
        serializer.save(user=user)


class UserServiceListAPIView(generics.ListAPIView):
      serializer_class =ServiceListSerializer
      permission_classes = [IsAuthenticated]
            
      def get_queryset(self):
          return Service.objects.filter(user=self.request.user,is_active=True).select_related("category").order_by("-created_at")


class ServiceDetailAPIView(generics.RetrieveAPIView):
    serializer_class =ServiceDetailSerializer
    permission_classes =[IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return Service.objects.filter(user=self.request.user,is_active = True).select_related("category")


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
                {"detail": "Service deleted successfully."}, 
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Service not found or already deleted."}, 
                status=status.HTTP_404_NOT_FOUND
            )
