from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, PermissionDenied
from .serializers import (
    AccountantProfileSerializer,
    ClientProfileSerializer,
    AcademicProfileSerializer,
)
from .models import AccountantProfile, ClientProfile, AcademicProfile


# Accountant Profile Views
class AccountantProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AccountantProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  
    queryset = AccountantProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return AccountantProfile.objects.get(user=user)
        except AccountantProfile.DoesNotExist:
            raise NotFound("Profile not found.")

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()


# Client Profile Views
class ClientProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 
    queryset = ClientProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            raise NotFound("Profile not found.")

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()


# Academic Profile Views
class AcademicProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AcademicProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  
    queryset = AcademicProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return AcademicProfile.objects.get(user=user)
        except AcademicProfile.DoesNotExist:
            raise NotFound("Profile not found.")

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()
