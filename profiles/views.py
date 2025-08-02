from rest_framework import views
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import AccountantProfileSerializer
from .models import AccountantProfile
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError


class AccountantProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = AccountantProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = AccountantProfile.objects.all()

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type.lower() != "accountant":
            raise PermissionDenied("Only accountants can access profiles.")

        if AccountantProfile.objects.filter(user_id=user).exists():
            raise ValidationError("Profile allready exist !")

        serializer.save(user_id=user)


class AccountantProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AccountantProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "profile_id"
    queryset = AccountantProfile.objects.all()

    def get_object(self):
        user = self.request.user
        if user.user_type.lower() != "accountant":
            raise PermissionDenied("Only accountants can access profiles.")

        try:
            return AccountantProfile.objects.get(user_id=user)
        except AccountantProfile.DoesNotExist:
            raise NotFound("Profile not found. Please create a profile first.")

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user:
            raise PermissionError("You do not have permission to update this profile.")
        serializer.save()
