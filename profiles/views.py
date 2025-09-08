from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from .serializers import AccountantProfileSerializer, ClientProfileSerializer, AcademicProfileSerializer
from .models import AccountantProfile, ClientProfile, AcademicProfile


# Accountant Profile Views
class AccountantProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = AccountantProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = AccountantProfile.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.user_type != 'accountant':
            raise PermissionDenied("Only accountants can create accountant profiles.")

        if AccountantProfile.objects.filter(user_id=user).exists():
            raise ValidationError("Profile already exists!")

        serializer.save(user_id=user)


class AccountantProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AccountantProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = AccountantProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return AccountantProfile.objects.get(user_id=user)
        except AccountantProfile.DoesNotExist:
            raise NotFound("Profile not found. Please create a profile first.")

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()


# Client Profile Views
class ClientProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = ClientProfile.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.user_type != 'client':
            raise PermissionDenied("Only clients can create client profiles.")

        if ClientProfile.objects.filter(user_id=user).exists():
            raise ValidationError("Profile already exists!")

        serializer.save(user_id=user)


class ClientProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = ClientProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return ClientProfile.objects.get(user_id=user)
        except ClientProfile.DoesNotExist:
            raise NotFound("Profile not found. Please create a profile first.")

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()


# Academic Profile Views
class AcademicProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = AcademicProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = AcademicProfile.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.user_type != 'academic':
            raise PermissionDenied("Only academics can create academic profiles.")

        if AcademicProfile.objects.filter(user_id=user).exists():
            raise ValidationError("Profile already exists!")

        serializer.save(user_id=user)


class AcademicProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AcademicProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = AcademicProfile.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            return AcademicProfile.objects.get(user_id=user)
        except AcademicProfile.DoesNotExist:
            raise NotFound("Profile not found. Please create a profile first.")

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()
